"""
Tests that user and write tools report which Odoo url/db they used
"""

import pytest
from biszx_odoo_mcp.server import tools


@pytest.fixture
def mcp(mock_mcp_server_for_tools):
    """MCP server mock whose client is connected to a known url/db"""
    odoo = mock_mcp_server_for_tools.get_context().request_context.lifespan_context.odoo
    odoo.config.url = "https://test.odoo.com"
    odoo.config.db = "test_db"
    return mock_mcp_server_for_tools


def get_odoo(mcp):
    return mcp.get_context().request_context.lifespan_context.odoo


CONNECTION = {"url": "https://test.odoo.com", "db": "test_db"}


@pytest.mark.asyncio
async def test_get_current_user_includes_connection(mcp):
    user = {"id": 2, "name": "Admin"}
    get_odoo(mcp).get_current_user.return_value = user

    result = (await tools.get_current_user(mcp)).to_dict()

    assert result["data"] == {**user, **CONNECTION}
    assert user == {"id": 2, "name": "Admin"}  # cached user not mutated


@pytest.mark.asyncio
async def test_create_records_includes_connection(mcp):
    get_odoo(mcp).create_records.return_value = [6, 7]

    result = (await tools.create_records(mcp, "crm.lead", [{}, {}])).to_dict()

    assert result["data"] == {**CONNECTION, "model": "crm.lead", "ids": [6, 7]}


@pytest.mark.asyncio
async def test_create_records_single_id_is_a_list(mcp):
    get_odoo(mcp).create_records.return_value = 6

    result = (await tools.create_records(mcp, "crm.lead", [{}])).to_dict()

    assert result["data"]["ids"] == [6]


@pytest.mark.asyncio
async def test_write_records_includes_connection(mcp):
    get_odoo(mcp).write_records.return_value = True

    result = (await tools.write_records(mcp, "crm.lead", [6], {"name": "x"})).to_dict()

    assert result["data"] == {
        "success": True,
        **CONNECTION,
        "model": "crm.lead",
        "ids": [6],
    }


@pytest.mark.asyncio
async def test_search_and_write_includes_connection(mcp):
    odoo = get_odoo(mcp)
    odoo.search_ids.return_value = [6, 7]

    result = (
        await tools.search_and_write(mcp, "crm.lead", [], {"name": "x"})
    ).to_dict()

    assert result["data"] == {
        "affected_records": 2,
        "record_ids": [6, 7],
        **CONNECTION,
        "model": "crm.lead",
    }


@pytest.mark.asyncio
async def test_search_and_write_no_records_includes_connection(mcp):
    get_odoo(mcp).search_ids.return_value = []

    result = (
        await tools.search_and_write(mcp, "crm.lead", [], {"name": "x"})
    ).to_dict()

    assert result["data"]["affected_records"] == 0
    assert result["data"]["db"] == "test_db"
    assert result["data"]["model"] == "crm.lead"
