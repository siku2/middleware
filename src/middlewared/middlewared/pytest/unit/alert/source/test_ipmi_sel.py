from datetime import datetime
import textwrap

import pytest

from middlewared.alert.source.ipmi_sel import (
    IPMISELRecord, parse_ipmitool_output, parse_sel_information,
    IPMISELAlertSource, IPMISELSpaceLeftAlertSource,
    Alert
)


def test__parse_ipmitool_output():
    events = parse_ipmitool_output(textwrap.dedent("""\
        9,04/20/2017,06:03:07,Watchdog2 #0xca,Timer interrupt (),Asserted
        a,07/05/2017,03:17:30,Temperature PECI CPU1,Upper Non-critical going high,Asserted,Reading 144 > Threshold 81 degrees C
    """))

    assert events[0] == IPMISELRecord(
        id=9,
        datetime=datetime(2017, 4, 20, 6, 3, 7),
        sensor="Watchdog2 #0xca",
        event="Timer interrupt ()",
        direction="Asserted",
        verbose=None
    )

    assert events[1] == IPMISELRecord(
        id=10,
        datetime=datetime(2017, 7, 5, 3, 17, 30),
        sensor="Temperature PECI CPU1",
        event="Upper Non-critical going high",
        direction="Asserted",
        verbose="Reading 144 > Threshold 81 degrees C"
    )


def test__parse_sel_information():
    info = parse_sel_information(textwrap.dedent("""\
        SEL Information
        Version          : 1.5 (v1.5, v2 compliant)
        Entries          : 19
        Free Space       : 9860 bytes
        Percent Used     : 2%
        Last Add Time    : 07/05/2018 23:32:08
        Last Del Time    : Not Available
        Overflow         : false
        Supported Cmds   : 'Reserve' 'Get Alloc Info'
        # of Alloc Units : 512
        Alloc Unit Size  : 20
        # Free Units     : 493
        Largest Free Blk : 493
        Max Record Size  : 20
    """))

    assert info["Free Space"] == "9860 bytes"
    assert info["Percent Used"] == "2%"


@pytest.mark.asyncio
async def test_ipmi_sel_alert_source__works():
    assert await IPMISELAlertSource(None)._produce_alerts_for_ipmitool_output(textwrap.dedent("""\
        9,04/20/2017,06:03:07,Watchdog2 #0xca,Timer interrupt (),Asserted
    """)) == [
        Alert(
            title="%(sensor)s %(direction)s %(event)s",
            args=dict(
                sensor="Watchdog2 #0xca",
                event="Timer interrupt ()",
                direction="Asserted",
                verbose=None
            ),
            datetime=datetime(2017, 4, 20, 6, 3, 7),
        )
    ]


def test_ipmi_sel_space_left_alert_source__does_not_emit():
    assert IPMISELSpaceLeftAlertSource(None)._produce_alert_for_ipmitool_output(textwrap.dedent("""\
        SEL Information
        Version          : 1.5 (v1.5, v2 compliant)
        Entries          : 19
        Free Space       : 9860 bytes
        Percent Used     : 2%
        Last Add Time    : 07/05/2018 23:32:08
        Last Del Time    : Not Available
        Overflow         : false
        Supported Cmds   : 'Reserve' 'Get Alloc Info'
        # of Alloc Units : 512
        Alloc Unit Size  : 20
        # Free Units     : 493
        Largest Free Blk : 493
        Max Record Size  : 20
    """)) is None


def test_ipmi_sel_space_left_alert_source__emits():
    assert IPMISELSpaceLeftAlertSource(None)._produce_alert_for_ipmitool_output(textwrap.dedent("""\
        SEL Information
        Version          : 1.5 (v1.5, v2 compliant)
        Entries          : 19
        Free Space       : 260 bytes
        Percent Used     : 98%
        Last Add Time    : 07/05/2018 23:32:08
        Last Del Time    : Not Available
        Overflow         : false
        Supported Cmds   : 'Reserve' 'Get Alloc Info'
        # of Alloc Units : 512
        Alloc Unit Size  : 20
        # Free Units     : 493
        Largest Free Blk : 493
        Max Record Size  : 20
    """)) == Alert(
        title="IPMI SEL Low Space Left: %(free)s (used %(used)s)",
        args={
            "free": "260 bytes",
            "used": "98%",
        },
        key=None,
    )
