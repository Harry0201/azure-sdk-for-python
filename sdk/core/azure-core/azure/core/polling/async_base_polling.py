# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from ..exceptions import HttpResponseError
from .base_polling import (
    failed,
    BadStatus,
    BadResponse,
    OperationFailed,
    LROBasePolling,
    _raise_if_bad_http_status_and_method
)

__all__ = ["AsyncLROBasePolling"]

class AsyncLROBasePolling(LROBasePolling):
    """A subclass or LROBasePolling that redefine "run" as async.
    """

    async def run(self):
        try:
            await self._poll()
        except BadStatus as err:
            self._status = 'Failed'
            raise HttpResponseError(response=self._pipeline_response.http_response, error=err)

        except BadResponse as err:
            self._status = 'Failed'
            raise HttpResponseError(response=self._pipeline_response.http_response, message=str(err), error=err)

        except OperationFailed as err:
            raise HttpResponseError(response=self._pipeline_response.http_response, error=err)

    async def _poll(self):
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :param callable update_cmd: The function to call to retrieve the
         latest status of the long running operation.
        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """

        while not self.finished():
            await self._delay()
            await self.update_status()

        if failed(self.status()):
            raise OperationFailed("Operation failed or canceled")

        elif self._operation.should_do_final_get():
            request = self._initial_response.http_response.request
            if request.method == 'POST' and 'location' in self._initial_response.http_response.headers:
                final_get_url = self._initial_response.http_response.headers['location']
            else:
                final_get_url = request.url

            self._pipeline_response = await self.request_status(final_get_url)
            _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)

    async def _sleep(self, delay):
        await self._transport.sleep(delay)

    async def _delay(self):
        """Check for a 'retry-after' header to set timeout,
        otherwise use configured timeout.
        """
        if self._pipeline_response is None:
            return
        response = self._pipeline_response.http_response
        if response.headers.get('retry-after'):
            await self._sleep(int(response.headers['retry-after']))
        else:
            await self._sleep(self._timeout)

    async def update_status(self):
        """Update the current status of the LRO.
        """
        self._pipeline_response = await self.request_status(self._operation.get_polling_url())
        _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)
        self._status = self._operation.get_status(self._pipeline_response)

    async def request_status(self, status_link):
        """Do a simple GET to this status link.

        This method re-inject 'x-ms-client-request-id'.

        :rtype: azure.core.pipeline.PipelineResponse
        """
        request = self._client.get(status_link)
        # Re-inject 'x-ms-client-request-id' while polling
        if 'request_id' not in self._operation_config:
            self._operation_config['request_id'] = self._get_request_id()
        return await self._client._pipeline.run(request, stream=False, **self._operation_config)  # pylint: disable=protected-access
