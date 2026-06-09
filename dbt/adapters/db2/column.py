# -------------------------------------------------------------------------------------------------#
#                      DISCLAIMER OF WARRANTIES AND LIMITATION OF LIABILITY                       #
#                                                                                                 #
#  (C) COPYRIGHT International Business Machines Corp. 2026 All Rights Reserved             #
#  Licensed Materials - Property of IBM                                                           #
#                                                                                                 #
#  US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP   #
#  Schedule Contract with IBM Corp.                                                               #
#                                                                                                 #
#  The following source code ("Sample") is owned by International Business Machines Corporation   #
#  or one of its subsidiaries ("IBM") and is copyrighted and licensed, not sold. You may use,     #
#  copy, modify, and distribute the Sample in any form without payment to IBM, for the purpose    #
#  of assisting you in the creation of Python applications using the ibm_db library.              #
#                                                                                                 #
#  The Sample code is provided to you on an "AS IS" basis, without warranty of any kind. IBM      #
#  HEREBY EXPRESSLY DISCLAIMS ALL WARRANTIES, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT       #
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.    #
#  Some jurisdictions do not allow for the exclusion or limitation of implied warranties, so the  #
#  above limitations or exclusions may not apply to you. IBM shall not be liable for any damages  #
#  you suffer as a result of using, copying, modifying or distributing the Sample, even if IBM    #
#  has been advised of the possibility of such damages.                                           #
# -------------------------------------------------------------------------------------------------#

from dbt.adapters.base.column import Column
from dataclasses import dataclass


@dataclass
class Db2Column(Column):
    TYPE_LABELS = {
        **Column.TYPE_LABELS,
        "STRING": "varchar(2000)",
    }

    # Override to ignore data type length
    def is_string(self) -> bool:
        return self.dtype.lower() == "text" or any(
            self.dtype.lower().startswith(dtype)
            for dtype in ["char", "nchar", "varchar", "nvarchar"]
        )

    # Override to ignore data type precision
    def is_numeric(self) -> bool:
        return any(
            self.dtype.lower().startswith(dtype) for dtype in ["numeric", "decimal"]
        )
