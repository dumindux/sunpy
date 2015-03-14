import datetime
import pytest

from sunpy.time.timerange import TimeRange
from sunpy.net.vso.attrs import Time, Instrument, Level
from sunpy.net.dataretriever.client import QueryResponse
import sunpy.net.dataretriever.sources.noaa as noaa

LCClient = noaa.NOAAPredictClient()

@pytest.mark.parametrize("timerange,url",
                         [(TimeRange('2015/2/21', '2015/2/21'),
                           "http://services.swpc.noaa.gov/text/predicted-sunspot-radio-flux.txt"),
                          (TimeRange('2015/3/5', '2015/3/6'),
                           "http://services.swpc.noaa.gov/text/predicted-sunspot-radio-flux.txt"),
                          (TimeRange('2015/1/7', '2015/1/14'),
                           "http://services.swpc.noaa.gov/text/predicted-sunspot-radio-flux.txt")
                         ])
def test_get_url_for_time_range(timerange, url):
    urls = LCClient._get_url_for_timerange(timerange)
    assert isinstance(urls, list)
    assert urls[0] == url


@pytest.mark.parametrize("url",
                         ["http://services.swpc.noaa.gov/text/predicted-sunspot-radio-flux.txt"])
def test_fail_get_url_for_time_range(url):
    urls = LCClient._get_url_for_timerange(None)
    assert isinstance(urls, list)
    assert len(urls) == 1
    assert urls[0] == url

def test_get_url_for_date():
    with pytest.raises(NotImplementedError):
        url = LCClient._get_url_for_date(datetime.date(2015, 2, 15))

def test_can_handle_query():
    ans1 = noaa.NOAAPredictClient._can_handle_query(Time('2015/01/9', '2015/02/10'), Instrument('noaa-predict'), Level(0))
    assert ans1 is False
    ans2 = noaa.NOAAPredictClient._can_handle_query(Time('2015/01/9', '2015/02/10'))
    assert ans2 is False
    ans3 = noaa.NOAAPredictClient._can_handle_query(Time('2015/01/9', '2015/02/10'), Instrument('noaa-predict'))
    assert ans3 is True

def test_query():
    qr1 = LCClient.query(Time('2015/01/9', '2015/02/10'), Instrument('noaa-predict'))
    assert isinstance(qr1, QueryResponse)
    assert len(qr1) == 1
    assert qr1.time_range()[0] == '2015/01/09'
    assert qr1.time_range()[1] == '2015/02/10'


@pytest.mark.online
@pytest.mark.parametrize("time,instrument",
                         [(Time('2015/01/27', '2015/02/27'), Instrument('noaa-indices')),
                          (Time('2015/01/04', '2012/02/06'), Instrument('noaa-indices')),
                          ])
def test_get(time, instrument):
    qr1 = LCClient.query(time, instrument)
    res = LCClient.get(qr1)
    download_list = res.wait()
    assert len(download_list) == len(qr1)

