# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from .offer_term_info import OfferTermInfo


class MonetaryCommitment(OfferTermInfo):
    """Indicates that a monetary commitment is required for this offer.

    :param effective_date: Indicates the date from which the offer term is
     effective.
    :type effective_date: datetime
    :param name: Constant filled by server.
    :type name: str
    :param tiered_discount: The list of key/value pairs for the tiered meter
     rates, in the format 'key':'value' where key = price, and value = the
     corresponding discount percentage. This field is used only by offer terms
     of type 'Monetary Commitment'.
    :type tiered_discount: dict[str, decimal.Decimal]
    :param excluded_meter_ids: An array of meter ids that are excluded from
     the given offer terms.
    :type excluded_meter_ids: list[str]
    """

    _validation = {
        'name': {'required': True},
    }

    _attribute_map = {
        'effective_date': {'key': 'EffectiveDate', 'type': 'iso-8601'},
        'name': {'key': 'Name', 'type': 'str'},
        'tiered_discount': {'key': 'TieredDiscount', 'type': '{decimal}'},
        'excluded_meter_ids': {'key': 'ExcludedMeterIds', 'type': '[str]'},
    }

    def __init__(self, effective_date=None, tiered_discount=None, excluded_meter_ids=None):
        super(MonetaryCommitment, self).__init__(effective_date=effective_date)
        self.tiered_discount = tiered_discount
        self.excluded_meter_ids = excluded_meter_ids
        self.name = 'Monetary Commitment'