"""
U8 SQL Server 连接与数据提取模块
"""

import pymssql
from typing import List, Dict, Any


EXTRACT_SQL = """
SELECT
    i.cInvCode       AS material_code,
    i.cInvName       AS material_name,
    i.cInvCCode      AS inv_class_code,
    ic.cInvCName     AS inv_class_name,
    i.cInvStd        AS specification,
    i.cComUnitCode   AS com_unit_code,
    cu.cComUnitName  AS com_unit_name,
    i.cInvDefine10   AS cloth_card_no,
    i.cInvDefine5    AS color_desc,
    i.cInvDefine7    AS remark,
    i.cInvDefine1    AS size_model,
    i.cInvDefine2    AS craft_desc,
    i.cInvDefine3    AS material_desc,
    i.cInvDefine6    AS market_desc,
    i.cInvDefine9    AS package_size
FROM Inventory i
LEFT JOIN InventoryClass ic
    ON i.cInvCCode = ic.cInvCCode
LEFT JOIN ComputationUnit cu
    ON i.cComUnitCode = cu.cComunitCode
WHERE 1 = 1
"""

MODIFIED_COLUMNS = ("dModifyDate", "dModifyTime", "dUpdateDate", "dEditDate", "dCreateDate")


def _inventory_columns(cursor) -> set:
    cursor.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'Inventory'
        """
    )
    return {row["COLUMN_NAME"] for row in cursor.fetchall()}


def _modified_column(columns: set) -> str:
    for column in MODIFIED_COLUMNS:
        if column in columns:
            return column
    return ""


def fetch_materials(
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    modified_after: str = "",
) -> List[Dict[str, Any]]:
    """
    连接 U8 SQL Server，执行抽取 SQL，返回物料列表。
    每条记录字段名与外网表字段名一致。
    """
    conn = pymssql.connect(
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
    try:
        with conn.cursor(as_dict=True) as cursor:
            sql = EXTRACT_SQL
            params = ()
            if modified_after:
                column = _modified_column(_inventory_columns(cursor))
                if not column:
                    raise RuntimeError("U8 Inventory 表未找到可用于增量同步的修改时间字段")
                sql = f"{EXTRACT_SQL}\nAND i.{column} >= %s"
                params = (modified_after,)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        return rows
    finally:
        conn.close()
