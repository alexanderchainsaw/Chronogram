import pytest
from chronogram.handlers.timecapsule.helpers import (_parse_datetime_from_message, _parse_date_from_message,
                                                     _parse_content_from_message)


@pytest.mark.asyncio
async def test_parse_content():
    assert await _parse_content_from_message(raw_text='') == ''
    assert await _parse_content_from_message(raw_text='Prompt date message') == ''
    assert await _parse_content_from_message(raw_text='somecontent\n\nsomedata') == 'somecontent'
    assert await _parse_content_from_message(raw_text='\n\n\n\n\n\n') == '\n\n\n\n'


@pytest.mark.asyncio
async def test_parse_date():
    assert await _parse_date_from_message(raw_text='Sample time capsule text\n\n'
                                                   'You have chosen 12.12.2012\n'
                                                   'Now select time') == '12.12.2012'
    assert await _parse_date_from_message(raw_text='You have chosen 12.12.2012\n'
                                                   'Now select time') == '12.12.2012'
    assert await _parse_date_from_message(raw_text='Контент для капсулы времени\n\n'
                                                   'Вы выбрали 12.12.2012\n'
                                                   'Теперь выберете время') == '12.12.2012'
    assert await _parse_date_from_message(raw_text='Вы выбрали 12.12.2012\n'
                                                   'Теперь выберете время') == '12.12.2012'


@pytest.mark.asyncio
async def test_parse_datetime():
    assert await _parse_datetime_from_message(raw_text='Ваша капсула времени будет доставлена:\n'
                                                       '12.12.2012 12:12') == ['12.12.2012', '12:12']
    assert await _parse_datetime_from_message(raw_text='Your time capsule will be delivered on:\n'
                                                       '12.12.2012 12:12') == ['12.12.2012', '12:12']
    with pytest.raises(RuntimeError):
        await _parse_datetime_from_message(raw_text='Only date\n12.12.2012')
        await _parse_datetime_from_message(raw_text='Only time\n12:12')
