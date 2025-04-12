# Legal Disclaimer
# This script is an example script and is not supported under any Zerto support program or service. 
# The author and Zerto further disclaim all implied warranties including, without limitation, 
# any implied warranties of merchantability or of fitness for a particular purpose.
# In no event shall Zerto, its authors or anyone else involved in the creation, 
# production or delivery of the scripts be liable for any damages whatsoever (including, 
# without limitation, damages for loss of business profits, business interruption, loss of business 
# information, or other pecuniary loss) arising out of the use of or the inability to use the sample 
# scripts or documentation, even if the author or Zerto has been advised of the possibility of such damages. 
# The entire risk arising out of the use or performance of the sample scripts and documentation remains with you.

from enum import Enum

class ZertoTaskTypes(Enum):
    CreateProtectionGroup = 0
    RemoveProtectionGroup = 1
    FailOver = 2
    FailOverTest = 3
    StopFailOverTest = 4
    Move = 5
    GetCheckpointList = 6
    ProtectVM = 7
    UnprotectVM = 8
    AddVMToProtectionGroup = 9
    RemoveVMFromProtectionGroup = 10
    InstallVra = 11
    UninstallVra = 12
    GetVMSettings = 13
    UpdateProtectionGroup = 14
    InsertTaggedCP = 15
    WaitForCP = 16
    HandleMirrorPromotion = 17
    ActivateAllMirrors = 18
    LogCollection = 19
    ClearCheckpoints = 20
    ForceReconfigurationOfNewVM = 21
    ClearSite = 22
    ForceRemoveProtectionGroup = 23
    ForceUpdateProtectionGroup = 24
    ForceKillProtectionGroup = 25
    PrePostScript = 26
    InitFullSync = 27
    Pair = 28
    Unpair = 29
    AddPeerVraInfo = 30
    RemovePeerVraInfo = 31
    InstallCloudConnector = 32
    UninstallCloudConnector = 33
    HandleFirstSyncDone = 34
    Clone = 35
    MoveBeforeCommit = 36
    MoveRollback = 37
    MoveCommit = 38
    UpgradeVRA = 39
    MaintainHost = 40
    NotSupportedInThisVersion = 41
    MoveProtectionGroupToManualOperationNeeded = 42
    FailoverBeforeCommit = 43
    FailoverCommit = 44

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

    @classmethod
    def get_value_by_name(cls, name):
        for member in cls:
            if member.name == name:
                return member.value
        return None

class ZertoTaskStates(Enum):
    FirstUnusedValue = 0
    InProgress = 1
    WaitingForUserInput = 2
    Paused = 3
    Failed = 4
    Stopped = 5
    Completed = 6
    Cancelling = 7

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

    @classmethod
    def get_value_by_name(cls, name):
        for member in cls:
            if member.name == name:
                return member.value
        return None

class ZertoVPGStatus(Enum):
    Initializing = 0
    MeetingSLA = 1
    NotMeetingSLA = 2
    HistoryNotMeetingSLA = 3
    RpoNotMeetingSLA = 4
    FailingOver = 5
    Moving = 6
    Deleting = 7
    Recovered = 8

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None
    
    @classmethod
    def get_value_by_name(cls, name):
        for member in cls:
            if member.name == name:
                return member.value
        return None

class ZertoVPGSubstatus(Enum):
    NONE = 0  # Using NONE instead of None as None is a Python keyword
    InitialSync = 1
    Creating = 2
    VolumeInitialSync = 3
    Sync = 4
    RecoveryPossible = 5
    DeltaSync = 6
    NeedsConfiguration = 7
    Error = 8
    EmptyProtectionGroup = 9
    DisconnectedFromPeerNoRecoveryPoints = 10
    FullSync = 11
    VolumeDeltaSync = 12
    VolumeFullSync = 13
    FailingOverCommitting = 14
    FailingOverBeforeCommit = 15
    FailingOverRollingBack = 16
    Promoting = 17
    MovingCommitting = 18
    MovingBeforeCommit = 19
    MovingRollingBack = 20
    Deleting = 21
    PendingRemove = 22
    BitmapSync = 23
    DisconnectedFromPeer = 24
    ReplicationPausedUserInitiated = 25
    ReplicationPausedSystemInitiated = 26
    RecoveryStorageProfileError = 27
    Backup = 28
    RollingBack = 29
    RecoveryStorageError = 30
    JournalStorageError = 31
    VmNotProtectedError = 32

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

    @classmethod
    def get_value_by_name(cls, name):
        for member in cls:
            if member.name == name:
                return member.value
        return None

class ZertoProtectedSiteType(Enum):
    VCVpg = 0
    VCvApp = 1
    VCDvApp = 2
    AWS = 3
    HyperV = 4 

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

    @classmethod
    def get_value_by_name(cls, name):
        for member in cls:
            if member.name == name:
                return member.value
        return None

class ZertoRecoverySiteType(Enum):
    VCVpg = 0
    VCvApp = 1
    VCDvApp = 2
    AWS = 3
    HyperV = 4

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

    @classmethod
    def get_value_by_name(cls, name):
        for member in cls:
            if member.name == name:
                return member.value
        return None

class ZertoVPGPriority(Enum):
    Low = 0
    Medium = 1
    High = 2

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoVRAStatus(Enum):
    Installed = 0
    UnsupportedEsxVersion = 1
    NotInstalled = 2
    Installing = 3
    Removing = 4
    InstallationError = 5
    HostPasswordChanged = 6
    UpdatingIpSettings = 7
    DuringChangeHost = 8

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoPairingStatus(Enum):
    Paired = 0
    Pairing = 1
    Unpaired = 2

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoAlertLevel(Enum):
    Warning = 0
    Error = 1

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoAlertEntity(Enum):
    Zvm = 0
    Vra = 1
    Vpg = 2
    CloudConnector = 3
    Storage = 4
    License = 5
    Zcm = 6
    FileRecoveryComponent = 7

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoAlertHelpIdentifier(Enum):
    AWS0001 = 0
    BCK0001 = 1
    BCK0002 = 2
    BCK0005 = 3
    BCK0006 = 4
    BCK0007 = 5
    LIC0001 = 6
    LIC0002 = 7
    LIC0003 = 8
    LIC0004 = 9
    LIC0005 = 10
    LIC0006 = 11
    LIC0007 = 12
    LIC0008 = 13
    STR0001 = 14
    STR0002 = 15
    STR0004 = 16
    VCD0001 = 17
    VCD0002 = 18
    VCD0003 = 19
    VCD0004 = 20
    VCD0005 = 21
    VCD0006 = 22
    VCD0007 = 23
    VCD0010 = 24
    VCD0014 = 25
    VCD0015 = 26
    VCD0016 = 27
    VCD0017 = 28
    VCD0018 = 29
    VCD0020 = 30
    VCD0021 = 31
    VPG0003 = 32
    VPG0004 = 33
    VPG0005 = 34
    VPG0006 = 35
    VPG0007 = 36
    VPG0008 = 37
    VPG0009 = 38
    VPG0010 = 39
    VPG0011 = 40
    VPG0012 = 41
    VPG0014 = 42
    VPG0015 = 43
    VPG0016 = 44
    VPG0017 = 45
    VPG0018 = 46
    VPG0019 = 47
    VPG0020 = 48
    VPG0021 = 49
    VPG0022 = 50
    VPG0023 = 51
    VPG0024 = 52
    VPG0025 = 53
    VPG0026 = 54
    VPG0027 = 55
    VPG0028 = 56
    VPG0035 = 57
    VPG0036 = 58
    VPG0037 = 59
    VPG0038 = 60
    VPG0039 = 61
    VPG0040 = 62
    VPG0041 = 63
    VPG0042 = 64
    VPG0043 = 65
    VPG0044 = 66
    VPG0045 = 67
    VPG0046 = 68
    VPG0047 = 69
    VPG0048 = 70
    VRA0001 = 71
    VRA0002 = 72
    VRA0003 = 73
    VRA0004 = 74
    VRA0005 = 75
    VRA0006 = 76
    VRA0007 = 77
    VRA0008 = 78
    VRA0009 = 79
    VRA0010 = 80
    VRA0011 = 81
    VRA0012 = 82
    VRA0013 = 83
    VRA0014 = 84
    VRA0015 = 85
    VRA0016 = 86
    VRA0017 = 87
    VRA0018 = 88
    VRA0019 = 89
    VRA0020 = 90
    VRA0021 = 91
    VRA0022 = 92
    VRA0023 = 93
    VRA0024 = 94
    VRA0025 = 95
    VRA0026 = 96
    VRA0027 = 97
    VRA0028 = 98
    VRA0029 = 99
    VRA0030 = 100
    VRA0032 = 101
    VRA0035 = 102
    VRA0036 = 103
    VRA0037 = 104
    VRA0038 = 105
    VRA0039 = 106
    VRA0040 = 107
    VRA0049 = 108
    VRA0050 = 109
    VRA0051 = 110
    VRA0052 = 111
    VRA0053 = 112
    VRA0054 = 113
    VRA0055 = 114
    ZCC0001 = 115
    ZCC0002 = 116
    ZCC0003 = 117
    ZCM0001 = 118
    ZVM0001 = 119
    ZVM0002 = 120
    ZVM0003 = 121
    ZVM0004 = 122
    ZVM0005 = 123
    ZVM0006 = 124
    ZVM0007 = 125
    ZVM0008 = 126
    ZVM0009 = 127
    ZVM0010 = 128
    ZVM0011 = 129
    ZVM0012 = 130
    ZVM0013 = 131
    ZVM0014 = 132
    ZVM0015 = 133
    FLR0001 = 134
    Unknown = 135

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoEventType(Enum):
    Unknown = 0
    CreateProtectionGroup = 1
    RemoveProtectionGroup = 2
    FailOver = 3
    FailOverTest = 4
    StopFailOverTest = 5
    Move = 6
    ProtectVM = 7
    UnprotectVM = 8
    InstallVra = 9
    UninstallVra = 10
    UpdateProtectionGroup = 11
    InsertTaggedCP = 12
    HandleMirrorPromotion = 13
    ActivateAllMirrors = 14
    LogCollection = 15
    ForceReconfigurationOfNewVM = 16
    ClearSite = 17
    ForceRemoveProtectionGroup = 18
    ForceUpdateProtectionGroup = 19
    ForceKillProtectionGroup = 20
    PrePostScript = 21
    InitFullSync = 22
    Pair = 23
    Unpair = 24
    InstallCloudConnector = 25
    UninstallCloudConnector = 26
    RedeployCloudConnector = 27
    ScriptExecutionFailure = 28
    SetAdvancedSiteSettings = 29
    Clone = 30
    KeepDisk = 31
    FailoverBeforeCommit = 32
    FailoverCommit = 33
    FailoverRollback = 34
    MoveBeforeCommit = 35
    MoveRollback = 36
    MoveCommit = 37
    MaintainHost = 38
    UpgradeVra = 39
    MoveProtectionGroupToManualOperationNeeded = 40
    ChangeVraIpSettings = 41
    PauseProtectionGroup = 42
    ResumeProtectionGroup = 43
    UpgradeZVM = 44
    BulkUpgradeVras = 45
    BulkUninstallVras = 46
    AlertTurnedOn = 47
    AlertTurnedOff = 48
    ChangeVraPassword = 49
    ChangeRecoveryHost = 50
    BackupProtectionGroup = 51
    CleanupProtectionGroupVipDiskbox = 52
    RestoreProtectionGroup = 53
    PreScript = 54
    PostScript = 55
    RemoveVmFromVc = 56
    ChangeVraPasswordIpSettings = 57
    FlrJournalMount = 58
    FlrJournalUnmount = 59
    Login = 60

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoEventCategory(Enum):
    All = 0
    Events = 1
    Alerts = 2

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoCommitPolicy(Enum):
    Rollback = 0
    Commit = 1
    NONE = 2  # Using NONE instead of None as None is a Python keyword

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoShutdownPolicy(Enum):
    NONE = 0  # Using NONE instead of None as None is a Python keyword
    Shutdown = 1
    ForceShutdown = 2

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoVRAIPConfigType(Enum):
    Dhcp = 0
    Static = 1

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoVPGSettingsBackupRetentionPeriod(Enum):
    OneWeek = 0
    OneMonth = 1
    ThreeMonths = 2
    SixMonths = 3
    NineMonths = 4
    OneYear = 5

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoVPGSettingsBackupSchedulerDOW(Enum):
    Sunday = 0
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoVPGSettingsBackupSchedulerPeriod(Enum):
    Daily = 0
    Weekly = 1

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None

class ZertoTweakType(Enum):
    ZVM = "zvm-tweak"
    VRA = "vra-tweak"
    Frontend = "frontend-tweak"

    @classmethod
    def get_name_by_value(cls, value):
        for member in cls:
            if member.value == value:
                return member.name
        return None
