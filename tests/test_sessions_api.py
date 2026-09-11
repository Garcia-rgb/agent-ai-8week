import httpx


async def test_list_sessions_is_paginated_and_user_scoped(client: httpx.AsyncClient) -> None:
    u1_session_ids = []
    for index in range(3):
        response = await client.post(
            "/chat",
            json={"message": f"普通问题 {index}", "user_id": "u1"},
        )
        u1_session_ids.append(response.json()["session_id"])

    await client.post(
        "/chat",
        json={"message": "另一个用户的问题", "user_id": "u2"},
    )

    first_page = await client.get(
        "/sessions",
        params={"limit": 2, "offset": 0},
        headers={"x-user-id": "u1"},
    )
    assert first_page.status_code == 200
    first_body = first_page.json()
    assert first_body["total"] == 3
    assert first_body["limit"] == 2
    assert first_body["offset"] == 0
    assert [item["id"] for item in first_body["items"]] == list(reversed(u1_session_ids))[:2]
    assert all(item["user_id"] == "u1" for item in first_body["items"])

    second_page = await client.get(
        "/sessions",
        params={"limit": 2, "offset": 2},
        headers={"x-user-id": "u1"},
    )
    assert second_page.status_code == 200
    assert len(second_page.json()["items"]) == 1


async def test_list_sessions_rejects_invalid_pagination(client: httpx.AsyncClient) -> None:
    invalid_limit = await client.get("/sessions", params={"limit": 0})
    invalid_offset = await client.get("/sessions", params={"offset": -1})

    assert invalid_limit.status_code == 422
    assert invalid_offset.status_code == 422

