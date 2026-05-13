"""
U8 SQL Server 库存台账查询模块。
扫码详情页实时读取 U8，只做只读查询，不写入业务库。
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List

import pymssql


_ALL_FLOW_CTE = """
;WITH AllFlow AS (
    SELECT
        R.cWhCode AS warehouse_code,
        CASE WHEN R.dnmaketime IS NOT NULL THEN R.dnmaketime ELSE CAST(R.dDate AS DATETIME) END AS document_date,
        CAST(R.dVeriDate AS DATETIME) AS verify_date,
        CASE WHEN R.dnverifytime IS NOT NULL THEN R.dnverifytime ELSE CAST(R.dVeriDate AS DATETIME) END AS verify_sort_time,
        R.cCode AS document_code,
        N'期初结存' AS document_type,
        CAST(ISNULL(RS.iQuantity, 0) AS DECIMAL(18,6)) AS in_quantity,
        CAST(0 AS DECIMAL(18,6)) AS out_quantity,
        CAST(ISNULL(RS.iQuantity, 0) AS DECIMAL(18,6)) AS quantity_change,
        CAST(RS.AutoID AS BIGINT) AS detail_id
    FROM rdrecord34 R
    INNER JOIN rdrecords34 RS ON R.ID = RS.ID
    WHERE RS.cInvCode = @cInvCode
      AND R.dVeriDate < DATEADD(DAY, 1, @EndDate)

    UNION ALL

    SELECT
        R.cWhCode,
        CASE WHEN R.dnmaketime IS NOT NULL THEN R.dnmaketime ELSE CAST(R.dDate AS DATETIME) END,
        CAST(R.dVeriDate AS DATETIME),
        CASE WHEN R.dnverifytime IS NOT NULL THEN R.dnverifytime ELSE CAST(R.dVeriDate AS DATETIME) END,
        R.cCode,
        N'采购入库单',
        CAST(ISNULL(RS.iQuantity, 0) AS DECIMAL(18,6)),
        CAST(0 AS DECIMAL(18,6)),
        CAST(ISNULL(RS.iQuantity, 0) AS DECIMAL(18,6)),
        CAST(RS.AutoID AS BIGINT)
    FROM rdrecord01 R
    INNER JOIN rdrecords01 RS ON R.ID = RS.ID
    WHERE RS.cInvCode = @cInvCode
      AND R.dVeriDate < DATEADD(DAY, 1, @EndDate)

    UNION ALL

    SELECT
        R.cWhCode,
        CASE WHEN R.dnmaketime IS NOT NULL THEN R.dnmaketime ELSE CAST(R.dDate AS DATETIME) END,
        CAST(R.dVeriDate AS DATETIME),
        CASE WHEN R.dnverifytime IS NOT NULL THEN R.dnverifytime ELSE CAST(R.dVeriDate AS DATETIME) END,
        R.cCode,
        N'调拨入库单',
        CAST(ISNULL(RS.iQuantity, 0) AS DECIMAL(18,6)),
        CAST(0 AS DECIMAL(18,6)),
        CAST(ISNULL(RS.iQuantity, 0) AS DECIMAL(18,6)),
        CAST(RS.AutoID AS BIGINT)
    FROM rdrecord08 R
    INNER JOIN rdrecords08 RS ON R.ID = RS.ID
    WHERE RS.cInvCode = @cInvCode
      AND R.dVeriDate < DATEADD(DAY, 1, @EndDate)

    UNION ALL

    SELECT
        R.cWhCode,
        CASE WHEN R.dnmaketime IS NOT NULL THEN R.dnmaketime ELSE CAST(R.dDate AS DATETIME) END,
        CAST(R.dVeriDate AS DATETIME),
        CASE WHEN R.dnverifytime IS NOT NULL THEN R.dnverifytime ELSE CAST(R.dVeriDate AS DATETIME) END,
        R.cCode,
        N'调拨出库单',
        CAST(0 AS DECIMAL(18,6)),
        CAST(ISNULL(RS.iQuantity, 0) AS DECIMAL(18,6)),
        CAST(-ISNULL(RS.iQuantity, 0) AS DECIMAL(18,6)),
        CAST(RS.AutoID AS BIGINT)
    FROM rdrecord09 R
    INNER JOIN rdrecords09 RS ON R.ID = RS.ID
    WHERE RS.cInvCode = @cInvCode
      AND R.dVeriDate < DATEADD(DAY, 1, @EndDate)

    UNION ALL

    SELECT
        R.cWhCode,
        CASE WHEN R.dnmaketime IS NOT NULL THEN R.dnmaketime ELSE CAST(R.dDate AS DATETIME) END,
        CAST(R.dVeriDate AS DATETIME),
        CASE WHEN R.dnverifytime IS NOT NULL THEN R.dnverifytime ELSE CAST(R.dVeriDate AS DATETIME) END,
        R.cCode,
        N'材料出库单',
        CAST(0 AS DECIMAL(18,6)),
        CAST(ISNULL(RS.iQuantity, 0) AS DECIMAL(18,6)),
        CAST(-ISNULL(RS.iQuantity, 0) AS DECIMAL(18,6)),
        CAST(RS.AutoID AS BIGINT)
    FROM rdrecord11 R
    INNER JOIN rdrecords11 RS ON R.ID = RS.ID
    WHERE RS.cInvCode = @cInvCode
      AND R.dVeriDate < DATEADD(DAY, 1, @EndDate)

    UNION ALL

    SELECT
        R.cWhCode,
        CASE WHEN R.dnmaketime IS NOT NULL THEN R.dnmaketime ELSE CAST(R.dDate AS DATETIME) END,
        CAST(R.dVeriDate AS DATETIME),
        CASE WHEN R.dnverifytime IS NOT NULL THEN R.dnverifytime ELSE CAST(R.dVeriDate AS DATETIME) END,
        R.cCode,
        N'销售出库单',
        CAST(0 AS DECIMAL(18,6)),
        CAST(ISNULL(RS.iQuantity, 0) AS DECIMAL(18,6)),
        CAST(-ISNULL(RS.iQuantity, 0) AS DECIMAL(18,6)),
        CAST(RS.AutoID AS BIGINT)
    FROM rdrecord32 R
    INNER JOIN rdrecords32 RS ON R.ID = RS.ID
    WHERE RS.cInvCode = @cInvCode
      AND R.dVeriDate < DATEADD(DAY, 1, @EndDate)
)
"""

_SUMMARY_SQL = """
DECLARE @cInvCode NVARCHAR(50)
DECLARE @StartDate DATETIME
DECLARE @EndDate DATETIME
SET @cInvCode = %s
SET @StartDate = %s
SET @EndDate = %s

""" + _ALL_FLOW_CTE + """
SELECT
    CAST(ISNULL(SUM(CASE WHEN verify_date < @StartDate THEN quantity_change ELSE 0 END), 0) AS DECIMAL(18,6)) AS opening_quantity,
    CAST(ISNULL(SUM(CASE WHEN verify_date >= @StartDate AND verify_date < DATEADD(DAY, 1, @EndDate) THEN in_quantity ELSE 0 END), 0) AS DECIMAL(18,6)) AS period_in_quantity,
    CAST(ISNULL(SUM(CASE WHEN verify_date >= @StartDate AND verify_date < DATEADD(DAY, 1, @EndDate) THEN out_quantity ELSE 0 END), 0) AS DECIMAL(18,6)) AS period_out_quantity,
    CAST(ISNULL(SUM(quantity_change), 0) AS DECIMAL(18,6)) AS ending_quantity
FROM AllFlow;
"""

_DETAIL_SQL = """
DECLARE @cInvCode NVARCHAR(50)
DECLARE @StartDate DATETIME
DECLARE @EndDate DATETIME
SET @cInvCode = %s
SET @StartDate = %s
SET @EndDate = %s

""" + _ALL_FLOW_CTE + """,
Opening AS (
    SELECT ISNULL(SUM(quantity_change), 0) AS opening_quantity
    FROM AllFlow
    WHERE verify_date < @StartDate
),
PeriodFlow AS (
    SELECT *
    FROM AllFlow
    WHERE verify_date >= @StartDate
      AND verify_date < DATEADD(DAY, 1, @EndDate)
),
FlowWithSeq AS (
    SELECT
        ROW_NUMBER() OVER (
            ORDER BY document_date, verify_sort_time, verify_date, detail_id
        ) AS seq,
        warehouse_code,
        document_date,
        verify_date,
        verify_sort_time,
        document_code,
        document_type,
        in_quantity,
        out_quantity,
        quantity_change,
        detail_id
    FROM PeriodFlow
)
SELECT
    A.warehouse_code,
    A.document_date,
    A.verify_date,
    A.document_code,
    A.document_type,
    A.in_quantity,
    A.out_quantity,
    CAST(O.opening_quantity + ISNULL((
        SELECT SUM(B.quantity_change)
        FROM FlowWithSeq B
        WHERE B.seq <= A.seq
    ), 0) AS DECIMAL(18,6)) AS balance_quantity
FROM FlowWithSeq A
CROSS JOIN Opening O
ORDER BY A.seq DESC;
"""


def _connect(host: str, port: int, database: str, user: str, password: str):
    return pymssql.connect(
        server=host,
        port=port,
        database=database,
        user=user,
        password=password,
        charset="UTF-8",
        tds_version="7.0",
        login_timeout=10,
        timeout=60,
    )


def _format_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return value


def _format_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {key: _format_value(value) for key, value in row.items()}


def fetch_inventory_ledger(
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    material_code: str,
    start_date: date,
    end_date: date,
) -> Dict[str, Any]:
    params = (
        material_code,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
    )

    conn = _connect(host, port, database, user, password)
    try:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute(_SUMMARY_SQL, params)
            summary = _format_row(cursor.fetchone() or {})

            cursor.execute(_DETAIL_SQL, params)
            items = [_format_row(row) for row in cursor.fetchall()]
    finally:
        conn.close()

    return {
        "material_code": material_code,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "summary": {
            "opening_quantity": summary.get("opening_quantity", 0),
            "period_in_quantity": summary.get("period_in_quantity", 0),
            "period_out_quantity": summary.get("period_out_quantity", 0),
            "ending_quantity": summary.get("ending_quantity", 0),
        },
        "items": items,
    }
