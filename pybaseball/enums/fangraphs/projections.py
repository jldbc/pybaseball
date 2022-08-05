from ..enum_base import EnumBase


class FangraphsProjections(EnumBase):
    # THE_BAT_X, THE_BAT_X_ROS, ON_PACE_GP don't work at the moment now
    ZIPS              = 'zips'
    ZIPSDC            = 'zipsdc'
    ZIPSP1            = 'zipsp1'
    ZIPSP2            = 'zipsp2'
    STEAMER           = 'steamer'
    STEAMER600        = 'steamer600'
    DEPTH_CHARTS      = 'fangraphsdc'
    ATC               = 'atc'
    THE_BAT           = 'thebat'
    # THE_BAT_X         = 'thebatx'
    ZIPS_ROS          = 'rzips'
    ZIPS_UPDATE       = 'uzips'
    STEAMER_ROS       = 'steamerr'
    STEAMER_UPDATE    = 'steameru'
    STEAMER600_UPDATE = 'steamer600u'
    DEPTH_CHARTS_ROS  = 'rfangraphsdc'
    THE_BAT_ROS       = 'rthebat'
    # THE_BAT_X_ROS     = 'rthebatros'
    ON_PACE_EGP       = 'onpaceegp'
    # ON_PACE_GP        = 'onpacegp'
