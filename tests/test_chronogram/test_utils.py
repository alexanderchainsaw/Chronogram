import pytest

from chronogram.utils import _format_user_space_remaining_percent, _format_user_space_remaining_mb


@pytest.mark.asyncio
async def test_format_percent():

    target_func = _format_user_space_remaining_percent

    assert await target_func(subscribed=True, space_taken=10000000) == '~0%'
    assert await target_func(subscribed=True, space_taken=9999999) == '~0%'
    assert await target_func(subscribed=True, space_taken=9900001) == '~0%'
    assert await target_func(subscribed=True, space_taken=9900000) == '~1%'

    assert await target_func(subscribed=False, space_taken=100000) == '~0%'
    assert await target_func(subscribed=False, space_taken=99999) == '~0%'
    assert await target_func(subscribed=False, space_taken=99001) == '~0%'
    assert await target_func(subscribed=False, space_taken=99000) == '~1%'

    assert await target_func(subscribed=False, space_taken=0) == '~100%'
    assert await target_func(subscribed=True, space_taken=0) == '~100%'

    assert await target_func(subscribed=False, space_taken=1) == '~99%'
    assert await target_func(subscribed=False, space_taken=1000) == '~99%'
    assert await target_func(subscribed=False, space_taken=1001) == '~98%'

    assert await target_func(subscribed=True, space_taken=1) == '~99%'
    assert await target_func(subscribed=True, space_taken=100000) == '~99%'
    assert await target_func(subscribed=True, space_taken=100001) == '~98%'


@pytest.mark.asyncio
async def test_format_mb():

    target_func = _format_user_space_remaining_mb

    assert await target_func(subscribed=True, space_taken=9999999) == '0.001<b>|</b>10MB'
    assert await target_func(subscribed=True, space_taken=10000000) == '0.000<b>|</b>10MB'

    assert await target_func(subscribed=True, space_taken=0) == '10<b>|</b>10MB'

    assert await target_func(subscribed=False, space_taken=99999) == '0.001<b>|</b>0.1MB'
    assert await target_func(subscribed=False, space_taken=100000) == '0.000<b>|</b>0.1MB'

    assert await target_func(subscribed=False, space_taken=0) == '0.1<b>|</b>0.1MB'



