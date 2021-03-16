import pandas as pd
from io import StringIO

from precip.transform import was_deleted

HEADER = [
    "Record-Type",
    "State-Code",
    "Cooperative Network Index Number",
    "Cooperative Network Division Number",
    "Element-Type",
    "Element-Units",
    "Number-Reported-Values",
    "Time-Of-Value",
    "Data-Value",
    "FLAG1",
    "date",
]
# Real example taken from October 1986 through March 1987 where the data
# between November 21-30 1986 was marked as deleted and then later the data
# between Navember 3 1986 and February 27 1987 was marked as deleted
NESTED_DELETES = """
1480,HPD,2,80,0,HPCP,HT,3,1300,10,,1986-10-09
1481,HPD,2,80,0,HPCP,HT,3,800,10,,1986-10-10
1482,HPD,2,80,0,HPCP,HT,2,100,0,g,1986-11-01
1483,HPD,2,80,0,HPCP,HT,3,400,99999,{,1986-11-03
1484,HPD,2,80,0,HPCP,HT,2,1600,99999,{,1986-11-21
1485,HPD,2,80,0,HPCP,HT,2,2400,99999,},1986-11-30
1486,HPD,2,80,0,HPCP,HT,2,100,0,g,1986-12-01
1487,HPD,2,80,0,HPCP,HT,3,700,10,,1986-12-06
1488,HPD,2,80,0,HPCP,HT,3,300,10,,1986-12-07
1489,HPD,2,80,0,HPCP,HT,2,1300,10,,1986-12-17
1490,HPD,2,80,0,HPCP,HT,2,1100,10,,1986-12-18
1491,HPD,2,80,0,HPCP,HT,2,1700,20,,1986-12-20
1492,HPD,2,80,0,HPCP,HT,2,1200,10,,1986-12-23
1493,HPD,2,80,0,HPCP,HT,2,100,0,g,1987-01-01
1494,HPD,2,80,0,HPCP,HI,3,600,10,,1987-01-05
1495,HPD,2,80,0,HPCP,HI,2,100,0,g,1987-02-01
1496,HPD,2,80,0,HPCP,HT,10,700,10,,1987-02-24
1497,HPD,2,80,0,HPCP,HT,3,800,99999,},1987-02-27
1498,HPD,2,80,0,HPCP,HT,2,100,0,g,1987-03-01
1499,HPD,2,80,0,HPCP,HT,2,100,0,g,1987-04-01
"""

# Real example where a station reports an end deletion bracket without a
# corresponding start deletion bracket
MISSING_START = """
9874,HPD,2,773,0,HPCP,HT,3,100,0,g,1993-01-01
9875,HPD,2,773,0,HPCP,HT,2,2400,99999,},1993-01-31
9876,HPD,2,773,0,HPCP,HT,3,100,0,g,1993-02-01
9877,HPD,2,773,0,HPCP,HT,2,1100,99999,],1993-02-02
"""

# Inverse of the real example
MISSING_END = """
9874,HPD,2,773,0,HPCP,HT,3,100,0,g,1993-01-01
9875,HPD,2,773,0,HPCP,HT,2,2400,99999,{,1993-01-31
9876,HPD,2,773,0,HPCP,HT,3,100,0,g,1993-02-01
9877,HPD,2,773,0,HPCP,HT,2,1100,99999,],1993-02-02
"""


def test_nested_deletes():
    """
    Test that the was_deleted function correctly flags deleted values.
    """
    df = pd.read_csv(StringIO(NESTED_DELETES), names=HEADER, index_col=0)

    delete_flag = was_deleted(df)
    assert all(delete_flag.loc[1483:1497].values == True)
    assert all(delete_flag.loc[1480:1482].values == False)
    assert all(delete_flag.loc[1498:1499].values == False)


def test_no_start():
    """
    Test that an end deletion bracket with no matching start bracket is
    simply marked as deleted.
    """
    df = pd.read_csv(StringIO(MISSING_START), names=HEADER, index_col=0)

    delete_flag = was_deleted(df)
    assert all(delete_flag.values == [False, True, False, False])


def test_no_end():
    """
    Test that a start deletion bracket with no matching end bracket is marked
    as deleted.
    """
    df = pd.read_csv(StringIO(MISSING_END), names=HEADER, index_col=0)

    delete_flag = was_deleted(df)
    assert all(delete_flag.values == [False, True, False, False])
