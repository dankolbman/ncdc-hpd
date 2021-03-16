import pandas as pd
from io import StringIO

from precip.transform import is_missing

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

# Adapted from the real example with missings. It's not clear if nested missing
# brackets are possible or make sense, but this ensures that the full superset
# is marked as missing
NESTED_MISSING = """
1480,HPD,2,80,0,HPCP,HT,3,1300,10,,1986-10-09
1481,HPD,2,80,0,HPCP,HT,3,800,10,,1986-10-10
1482,HPD,2,80,0,HPCP,HT,2,100,0,g,1986-11-01
1483,HPD,2,80,0,HPCP,HT,3,400,99999,[,1986-11-03
1484,HPD,2,80,0,HPCP,HT,2,1600,99999,[,1986-11-21
1485,HPD,2,80,0,HPCP,HT,2,2400,99999,],1986-11-30
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
1497,HPD,2,80,0,HPCP,HT,3,800,99999,],1987-02-27
1498,HPD,2,80,0,HPCP,HT,2,100,0,g,1987-03-01
1499,HPD,2,80,0,HPCP,HT,2,100,0,g,1987-04-01
"""

MISSING_START = """
9874,HPD,2,773,0,HPCP,HT,3,100,0,g,1993-01-01
9875,HPD,2,773,0,HPCP,HT,2,2400,99999,],1993-01-31
9876,HPD,2,773,0,HPCP,HT,3,100,0,g,1993-02-01
9877,HPD,2,773,0,HPCP,HT,2,1100,99999,g,1993-02-02
"""

MISSING_END = """
9874,HPD,2,773,0,HPCP,HT,3,100,0,g,1993-01-01
9875,HPD,2,773,0,HPCP,HT,2,2400,99999,[,1993-01-31
9877,HPD,2,773,0,HPCP,HT,2,1100,99999,g,1993-02-02
"""


def test_nested_missing():
    """
    Test that the is_missing function correctly flags nested missing values.
    """
    df = pd.read_csv(StringIO(NESTED_MISSING), names=HEADER, index_col=0)

    missing_flag = is_missing(df)
    assert all(missing_flag.loc[1483:1497].values == True)
    assert all(missing_flag.loc[1480:1482].values == False)
    assert all(missing_flag.loc[1498:1499].values == False)


def test_no_start():
    """
    Test that an end missing bracket with no matching start bracket is
    simply marked as missing.
    """
    df = pd.read_csv(StringIO(MISSING_START), names=HEADER, index_col=0)

    missing_flag = is_missing(df)
    assert all(missing_flag.values == [False, True, False, False])


def test_no_end():
    """
    Test that a start missing bracket with no matching end bracket is marked
    as missing.
    """
    df = pd.read_csv(StringIO(MISSING_END), names=HEADER, index_col=0)

    missing_flag = is_missing(df)
    assert all(missing_flag.values == [False, True, False])
