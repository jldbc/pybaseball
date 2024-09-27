from .fangraphs_stats_base import FangraphsStatsBase


class FangraphsPitchingStats(FangraphsStatsBase):
    COMMON                                 = 'c'
    LINE_BREAK                             = '-1'
    NAME                                   = '0'
    TEAM                                   = '1'
    SEASON                                 = '2'
    AGE                                    = '3'
    W                                      = '4'
    WINS                                   = W
    L                                      = '5'
    LOSSES                                 = L
    ERA                                    = '6'
    G                                      = '7'
    GAMES                                  = G
    GS                                     = '8'
    GAMES_SAVED                            = GS
    CG                                     = '9'
    COMPLETE_GAMES                         = CG
    SHO                                    = '10'
    SHUT_OUTS                              = SHO
    SV                                     = '11'
    SAVES                                  = SV
    BS                                     = '12' # ?
    IP                                     = '13'
    INNINGS_PITCHED                        = IP
    TBF                                    = '14' # ?
    H                                      = '15'
    HITS                                   = H
    R                                      = '16'
    RUNS                                   = R
    ER                                     = '17'
    EARNED_RUNS                            = ER
    HR                                     = '18'
    HOME_RUNS                              = HR
    BB                                     = '19'
    WALKS                                  = BB
    IBB                                    = '20'
    INTENTIONAL_WALKS                      = IBB
    HBP                                    = '21'
    HIT_BY_PITCH                           = HBP
    WP                                     = '22'
    WILD_PITCHES                           = WP
    BK                                     = '23'
    BALKS                                  = BK
    SO                                     = '24'
    STRIKE_OUTS                            = SO
    GB                                     = '25'
    GROUND_BALLS                           = GB
    FB                                     = '26'
    FLY_BALLS                              = FB
    LD                                     = '27' # ?
    IFFB                                   = '28' # ?
    BALLS                                  = '29'
    STRIKES                                = '30'
    PITCHES                                = '31'
    RS                                     = '32' # ?
    IFH                                    = '33' # ? INFIELD_HITS?
    BU                                     = '34' # ?
    BUH                                    = '35' # ?
    K_9                                    = '36' # K/9
    STRIKE_OUTS_PER_9_INNINGS              = K_9
    BB_9                                   = '37' # BB/9
    WALKS_PER_9_INNINGS                    = BB_9
    K_BB                                   = '38' # K/BB
    STRIKE_OUTS_PER_WALK                   = K_BB
    H_9                                    = '39' # H/9
    HITS_PER_9_INNINDS                     = H_9
    HR_9                                   = '40' # HR/9
    HOME_RUNS_PER_9_INNINGS                = HR_9
    AVG                                    = '41'
    BATTING_AVERAGE                        = AVG
    WHIP                                   = '42'
    WALKS_AND_HITS_PER_INNING_PITCHED      = WHIP
    BABIP                                  = '43'
    BATTING_AVERAGE_FOR_BALLS_IN_PLAY      = BABIP
    LOB_PCT                                = '44' # LOB%
    LEFT_ON_BASE_PERCENTAGE                = LOB_PCT
    FIP                                    = '45'
    FIELDING_INDEPENDENT_PITCHING          = FIP
    GB_FB                                  = '46' #GB/FB
    GROUND_BALLS_PER_FLY_BALL              = GB_FB
    LD_PCT                                 = '47' # LD% ?
    GB_PCT                                 = '48' # GB%
    GROUND_BALL_PERCENTAGE                 = GB_PCT
    FB_PCT                                 = '49' # FB%
    FLY_BALL_PERCENTAGE                    = FB_PCT
    IFFB_PCT                               = '50' # IFFB% ?
    HR_FB                                  = '51' # HR/FB
    HOME_RUNS_PER_FLY_BALL                 = HR_FB
    IFH_PCT                                = '52' # IFH%
    INFIELD_HIT_PERCENTAGE                 = IFH_PCT
    BUH_PCT                                = '53' # BUH% ?
    STARTING                               = '54'
    START_IP                               = '55' # Start-IP
    STARTING_INNINGS_PITCHED               = START_IP
    RELIEVING                              = '56'
    RELIEF_IP                              = '57'
    RELIEVING_INNINGS_PITCHED              = RELIEF_IP
    RAR                                    = '58'
    RUNS_ABOVE_REPLACEMENT                 = RAR
    WAR                                    = '59'
    WINS_ABOVE_REPLACEMENT                 = WAR
    DOLLARS                                = '60'
    DOLLARS_VALUE                          = DOLLARS
    TERA                                   = '61' # ?
    XFIP                                   = '62'
    EXPECTED_FIELDING_INDEPENDENT_PITCHING = XFIP
    WPA                                    = '63' #
    WIN_PROBABILITY_ADDED                  = WPA
    NEGATIVE_WPA                           = '64' # -WPA
    NEGATIVE_WIN_PROBABILITY_ADDED         = NEGATIVE_WPA
    POSITIVE_WPA                           = '65' # +WPA
    POSITIVE_WIN_PROBABILITY_ADDED         = POSITIVE_WPA
    RE24                                   = '66' # ?
    REW                                    = '67' # ?
    PLI                                    = '68' # ?
    INLI                                   = '69' # ?
    GMLI                                   = '70' # ?
    EXLI                                   = '71' # ?
    PULLS                                  = '72'
    WPA_LI                                 = '73' # WPA/LI ?
    CLUTCH                                 = '74'
    FB_PCT_PITCH                           = '75' # FB% (Pitch) ? Not sure the difference between this and the one in position 45
    FB_PCT_2                               = FB_PCT_PITCH
    FBV                                    = '76' # ?
    SL_PCT                                 = '77' # SL% ?
    SLV                                    = '78' # ?
    CT_PCT                                 = '79' # CT% ?
    CTV                                    = '80'
    CB_PCT                                 = '81' # CB% ?
    CBV                                    = '82' # ?
    CH_PCT                                 = '83' # CH% ?
    CHV                                    = '84' # ?
    SF_PCT                                 = '85' # SF% ?
    SFV                                    = '86' # ?
    KN_PCT                                 = '87' # KN% ?
    KNV                                    = '88' # ?
    XX_PCT                                 = '89' # XX% ?
    PO_PCT                                 = '90' # PO% ?
    WFB                                    = '91' # ?
    WSL                                    = '92' # ?
    WCT                                    = '93' # ?
    WCB                                    = '94' # ?
    WCH                                    = '95' # ?
    WSF                                    = '96' # ?
    WKN                                    = '97' # ?
    WFB_C                                  = '98' # wFB/C ?
    WSL_C                                  = '99' # wSL/C ?
    WCT_C                                  = '100' # wCT/C ?
    WCB_C                                  = '101' # wCB/C ?
    WCH_C                                  = '102' # wCH/C ?
    WSF_C                                  = '103' # wSF/C ?
    WKN_C                                  = '104' # wKN/C ?
    O_SWING_PCT                            = '105' # O-Swing% ?
    OSWING_PCT                             = O_SWING_PCT
    Z_SWING_PCT                            = '106' # Z-Swing% ?
    ZSWING_PCT                             = Z_SWING_PCT
    SWING_PCT                              = '107' # Swing% ?
    O_CONTACT_PCT                          = '108' # O-Contact% ?
    OCONTACT_PCT                           = O_CONTACT_PCT
    Z_CONTACT_PCT                          = '109' # Z-Contact% ?
    ZCONTACT_PCT                           = Z_CONTACT_PCT
    CONTACT_PCT                            = '110' # Contact% ?
    ZONE_PCT                               = '111' # Zone% ?
    F_STRIKE_PCT                           = '112' # F-Strike% ?
    FSTRIKE_PCT                            = F_STRIKE_PCT
    SWSTR_PCT                              = '113' # SwStr% SWINGING_STRIKE_PERCENTAGE?
    HLD                                    = '114' # HOLDS?
    SD                                     = '115' # ?
    MD                                     = '116' # ?
    ERA_MINUS                              = '117' # ERA- ?
    FIP_MINUS                              = '118' # FIP- ?
    XFIP_MINUS                             = '119' # xFIP- ?
    K_PCT                                  = '120' # K%
    STRIKE_OUT_PERCENTAGE                  = K_PCT
    BB_PCT                                 = '121' # BB%
    WALK_PERCENTAGE                        = BB_PCT
    SIERA                                  = '122' # ?
    RS_9                                   = '123'
    RUNS_SCORED_PER_9_INNINGS              = RS_9
    E_F                                    = '124' # E-F ?
    FA_PCT_SC                              = '125' # 'FA% (sc)' ?
    FT_PCT_SC                              = '126' # 'FT% (sc)' ?
    FC_PCT_SC                              = '127' # 'FC% (sc)' ?
    FS_PCT_SC                              = '128' # 'FS% (sc)' ?
    FO_PCT_SC                              = '129' # 'FO% (sc)' ?
    SI_PCT_SC                              = '130' # 'SI% (sc)' ?
    SL_PCT_SC                              = '131' # 'SL% (sc)' ?
    CU_PCT_SC                              = '132' # 'CU% (sc)' ?
    KC_PCT_SC                              = '133' # 'KC% (sc)' ?
    EP_PCT_SC                              = '134' # 'EP% (sc)' ?
    CH_PCT_SC                              = '135' # 'CH% (sc)' ?
    SC_PCT_SC                              = '136' # 'SC% (sc)' ?
    KN_PCT_SC                              = '137' # 'KN% (sc)' ?
    UN_PCT_SC                              = '138' # 'UN% (sc)' ?
    VFA_SC                                 = '139' # 'vFA (sc)' ?
    VFT_SC                                 = '140' # 'vFT (sc)' ?
    VFC_SC                                 = '141' # 'vFC (sc)' ?
    VFS_SC                                 = '142' # 'vFS (sc)' ?
    VFO_SC                                 = '143' # 'vFO (sc)' ?
    VSI_SC                                 = '144' # 'vSI (sc)' ?
    VSL_SC                                 = '145' # 'vSL (sc)' ?
    VCU_SC                                 = '146' # 'vCU (sc)' ?
    VKC_SC                                 = '147' # 'vKC (sc)' ?
    VEP_SC                                 = '148' # 'vEP (sc)' ?
    VCH_SC                                 = '149' # 'vCH (sc)' ?
    VSC_SC                                 = '150' # 'vSC (sc)' ?
    VKN_SC                                 = '151' # 'vKN (sc)' ?
    FA_X_SC                                = '152' # 'FA-X (sc)' ?
    FT_X_SC                                = '153' # 'FT-X (sc)' ?
    FC_X_SC                                = '154' # 'FC-X (sc)' ?
    FS_X_SC                                = '155' # 'FS-X (sc)' ?
    FO_X_SC                                = '156' # 'FO-X (sc)' ?
    SI_X_SC                                = '157' # 'SI-X (sc)' ?
    SL_X_SC                                = '158' # 'SL-X (sc)' ?
    CU_X_SC                                = '159' # 'CU-X (sc)' ?
    KC_X_SC                                = '160' # 'KC-X (sc)' ?
    EP_X_SC                                = '161' # 'EP-X (sc)' ?
    CH_X_SC                                = '162' # 'CG-X (sc)' ?
    SC_X_SC                                = '163' # 'SC-X (sc)' ?
    KN_X_SC                                = '164' # 'KN-X (sc)' ?
    FA_Z_SC                                = '165' # 'FA-Z (sc)' ?
    FT_Z_SC                                = '166' # 'FT-Z (sc)' ?
    FC_Z_SC                                = '167' # 'FC-Z (sc)' ?
    FS_Z_SC                                = '168' # 'FS-Z (sc)' ?
    FO_Z_SC                                = '169' # 'FO-Z (sc)' ?
    SI_Z_SC                                = '170' # 'SI-Z (sc)' ?
    SL_Z_SC                                = '171' # 'SL-Z (sc)' ?
    CU_Z_SC                                = '172' # 'CU-Z (sc)' ?
    KC_Z_SC                                = '173' # 'KC-Z (sc)' ?
    EP_Z_SC                                = '174' # 'EP-Z (sc)' ?
    CH_Z_SC                                = '175' # 'CH-Z (sc)' ?
    SC_Z_SC                                = '176' # 'SC-Z (sc)' ?
    KN_Z_SC                                = '177' # 'KN-Z (sc)' ?
    WFA_SC                                 = '178' # 'wFA (sc)' ?
    WFT_SC                                 = '179' # 'wFT (sc)' ?
    WFC_SC                                 = '180' # 'wFC (sc)' ?
    WFS_SC                                 = '181' # 'wFS (sc)' ?
    WFO_SC                                 = '182' # 'wFO (sc)' ?
    WSI_SC                                 = '183' # 'wSI (sc)' ?
    WSL_SC                                 = '184' # 'wSL (sc)' ?
    WCU_SC                                 = '185' # 'wCU (sc)' ?
    WKC_SC                                 = '186' # 'wKC (sc)' ?
    WEP_SC                                 = '187' # 'wEP (sc)' ?
    WCH_SC                                 = '188' # 'wCH (sc)' ?
    WSC_SC                                 = '189' # 'wSC (sc)' ?
    WKN_SC                                 = '190' # 'wKN (sc)' ?
    WFA_C_SC                               = '191' # 'wFA/C (sc)' ?
    WFT_C_SC                               = '192' # 'wFT/C (sc)' ?
    WFC_C_SC                               = '193' # 'wFC/C (sc)' ?
    WFS_C_SC                               = '194' # 'wFS/C (sc)' ?
    WFO_C_SC                               = '195' # 'wFO/C (sc)' ?
    WSI_C_SC                               = '196' # 'wSI/C (sc)' ?
    WSL_C_SC                               = '197' # 'wSL/C (sc)' ?
    WCU_C_SC                               = '198' # 'wCU/C (sc)' ?
    WKC_C_SC                               = '199' # 'wKC/C (sc)' ?
    WEP_C_SC                               = '200' # 'wEP/C (sc)' ?
    WCH_C_SC                               = '201' # 'wCH/C (sc)' ?
    WSC_C_SC                               = '202' # 'wSC/C (sc)' ?
    WKN_C_SC                               = '203' # 'wKN/C (sc)' ?
    O_SWING_PCT_SC                         = '204' # 'O-Swing% (sc)' ?
    Z_SWING_PCT_SC                         = '205' # 'Z-Swing% (sc)' ?
    SWING_PCT_SC                           = '206' # 'Swing% (sc)' ?
    O_CONTACT_PCT_SC                       = '207' # 'O-Contact% (sc)' ?
    Z_CONTACT_PCT_SC                       = '208' # 'Z-Contact% (sc)' ?
    CONTACT_PCT_SC                         = '209' # 'Contact% (sc)' ?
    ZONE_PCT_SC                            = '210' # 'Zone% (sc)' ?
    PACE                                   = '211'
    RA9_WAR                                = '212' # RA9-WAT ?
    BIP_WINS                               = '213' # BIP-Wins ?
    LOB_WINS                               = '214' # LOB-Wins ?
    FDP_WINS                               = '215' # FDP-Wins ?
    AGE_RNG                                = '216' # ?
    K_BB_PCT                               = '217' # ?
    PULL_PCT                               = '218' # ?
    CENT_PCT                               = '219' # ?
    OPPO_PCT                               = '220' # ?
    SOFT_PCT                               = '221' # ?
    MED_PCT                                = '222' # ?
    HARD_PCT                               = '223' # ?
    KWERA                                  = '224' # kwERA ?
    TTO_PCT                                = '225' # TTO% ?
    CH_PCT_PI                              = '226' # 'CH% (pi)' ?
    CS_PCT_PI                              = '227' # 'CS% (pi)' ?
    CU_PCT_PI                              = '228' # 'CU% (pi)' ?
    FA_PCT_PI                              = '229' # 'FA% (pi)' ?
    FC_PCT_PI                              = '230' # 'FC% (pi)' ?
    FS_PCT_PI                              = '231' # 'FS% (pi)' ?
    KN_PCT_PI                              = '232' # 'KN% (pi)' ?
    SB_PCT_PI                              = '233' # 'SB% (pi)' ?
    SI_PCT_PI                              = '234' # 'SI% (pi)' ?
    SL_PCT_PI                              = '235' # 'SL% (pi)' ?
    XX_PCT_PI                              = '236' # 'XX% (pi)' ?
    VCH_PI                                 = '237' # 'vCH (pi)' ?
    VCS_PI                                 = '238' # 'vCS (pi)' ?
    VCU_PI                                 = '239' # 'vCU (pi)' ?
    VFA_PI                                 = '240' # 'vFA (pi)' ?
    VFC_PI                                 = '241' # 'vFC (pi)' ?
    VFS_PI                                 = '242' # 'vFS (pi)' ?
    VKN_PI                                 = '243' # 'vKN (pi)' ?
    VSB_PI                                 = '244' # 'vSB (pi)' ?
    VSI_PI                                 = '245' # 'vSI (pi)' ?
    VSL_PI                                 = '246' # 'vSL (pi)' ?
    VXX_PI                                 = '247' # 'vXX (pi)' ?
    CH_X_PI                                = '248' # 'CH-X (pi)' ?
    CS_X_PI                                = '249' # 'CS-X (pi)' ?
    CU_X_PI                                = '250' # 'CU-X (pi)' ?
    FA_X_PI                                = '251' # 'FA-X (pi)' ?
    FC_X_PI                                = '252' # 'FC-X (pi)' ?
    FS_X_PI                                = '253' # 'FS-X (pi)' ?
    KN_X_PI                                = '254' # 'KN-X (pi)' ?
    SB_X_PI                                = '255' # 'SB-X (pi)' ?
    SI_X_PI                                = '256' # 'SI-X (pi)' ?
    SL_X_PI                                = '257' # 'SL-X (pi)' ?
    XX_X_PI                                = '258' # 'XX-X (pi)' ?
    CH_Z_PI                                = '259' # 'CH-Z (pi)' ?
    CS_Z_PI                                = '260' # 'CS-Z (pi)' ?
    CU_Z_PI                                = '261' # 'CU-Z (pi)' ?
    FA_Z_PI                                = '262' # 'FA-Z (pi)' ?
    FC_Z_PI                                = '263' # 'FC-Z (pi)' ?
    FS_Z_PI                                = '264' # 'FS-Z (pi)' ?
    KN_Z_PI                                = '265' # 'KN-Z (pi)' ?
    SB_Z_PI                                = '266' # 'SB-Z (pi)' ?
    SI_Z_PI                                = '267' # 'SI-Z (pi)' ?
    SL_Z_PI                                = '268' # 'SL-Z (pi)' ?
    XX_Z_PI                                = '269' # 'XX-Z (pi)' ?
    WCH_PI                                 = '270' # 'wCH (pi)' ?
    WCS_PI                                 = '271' # 'wCS (pi)' ?
    WCU_PI                                 = '272' # 'wCU (pi)' ?
    WFA_PI                                 = '273' # 'wFA (pi)' ?
    WFC_PI                                 = '274' # 'wFC (pi)' ?
    WFS_PI                                 = '275' # 'wFS (pi)' ?
    WKN_PI                                 = '276' # 'wKN (pi)' ?
    WSB_PI                                 = '277' # 'wSB (pi)' ?
    WSI_PI                                 = '278' # 'wSI (pi)' ?
    WSL_PI                                 = '279' # 'wSL (pi)' ?
    WXX_PI                                 = '280' # 'wXX (pi)' ?
    WCH_C_PI                               = '281' # 'wCH/C (pi)' ?
    WCS_C_PI                               = '282' # 'wCS/C (pi)' ?
    WCU_C_PI                               = '283' # 'wCU/C (pi)' ?
    WFA_C_PI                               = '284' # 'wFA/C (pi)' ?
    WFC_C_PI                               = '285' # 'wFC/C (pi)' ?
    WFS_C_PI                               = '286' # 'wFS/C (pi)' ?
    WKN_C_PI                               = '287' # 'wKN/C (pi)' ?
    WSB_C_PI                               = '288' # 'wSB/C (pi)' ?
    WSI_C_PI                               = '289' # 'wSI/C (pi)' ?
    WSL_C_PI                               = '290' # 'wSL/C (pi)' ?
    WXX_C_PI                               = '291' # 'wXX/C (pi)' ?
    O_SWING_PCT_PI                         = '292' # 'O-Swing% (sc)' ?
    OSWING_PCT_PI                          = O_SWING_PCT
    Z_SWING_PCT_PI                         = '293' # 'Z-Swing% (sc)' ?
    ZSWING_PCT_PI                          = Z_SWING_PCT_PI
    SWING_PCT_PI                           = '294' # 'Swing% (sc)' ?
    O_CONTACT_PCT_PI                       = '295' # 'O-Contact% (sc)' ?
    OCONTACT_PCT_PI                        = O_CONTACT_PCT_PI
    Z_CONTACT_PCT_PI                       = '296' # 'Z-Contact% (sc)' ?
    ZCONTACT_PCT_PI                        = Z_CONTACT_PCT_PI
    CONTACT_PCT_PI                         = '297' # 'Contact% (sc)' ?
    ZONE_PCT_PI                            = '298' # 'Zone% (sc)' ?
    PACE_PI                                = '299' # 'Pace (pi)'?
    FRAMING                                = '300' # Framing ?
    FRM                                    = FRAMING
    K_9_PLUS                               = '301' # K/9+ ?
    BB_9_PLUS                              = '302' # BB/9+ ?
    K_BB_PLUS                              = '303' # K/BB+ ?
    H_9_PLUS                               = '304' # H/9+ ?
    HR_9_PLUS                              = '305' # HR/9+ ?
    AVG_PLUS                               = '306' # AVG+ ?
    WHIP_PLUS                              = '307' # WHIP+ ?
    BABIP_PLUS                             = '308' # BABIP+ ?
    LOB_PCT_PLUS                           = '309' # LOB%+ ?
    K_PCT_PLUS                             = '310' # K%+ ?
    BB_PCT_PLUS                            = '311' # BB%+ ?
    LD_PCT_PLUS                            = '312' # LD%+ ?
    GB_PCT_PLUS                            = '313' # GB%+ ?
    FB_PCT_PLUS                            = '314' # FB%+ ?
    HR_FB_PCT_PLUS                         = '315' # HR/FB%+ ?
    PULL_PCT_PLUS                          = '316' # Pull%+ ?
    CENT_PCT_PLUS                          = '317' # Cent%+ ?
    OPPO_PCT_PLUS                          = '318' # Oppo%+ ?
    SOFT_PCT_PLUS                          = '319' # Soft%+ ?
    MED_PCT_PLUS                           = '320' # Med %+ ?
    HARD_PCT_PLUS                          = '321' # Hard%+ ?
    EV                                     = '322' # ?
    LA                                     = '323' # ?
    BARRELS                                = '324' # ?
    BARREL_PCT                             = '325' # Barrel% ?
    MAXEV                                  = '326' # maxEV ?
    HARDHIT                                = '327' # ?
    HARDHIT_PCT                            = '328' # HardHit% ?
    EVENTS                                 = '329' # ?
    CSTR_PCT                               = '330' # CStr% ?
    CSW_PCT                                = '331' # CSW% ?
    XERA                                   = '332' # xERA
    BOTERA                                 = '333' # botERA
    BOTOVR_CH                              = '334' # botOvr CH
    BOTSTF_CH                              = '335' # botStf CH
    BOTCMD_CH                              = '336' # botCmd CH
    BOTOVR_CU                              = '337' # botOvr CU
    BOTSTF_CU                              = '338' # botStf CU
    BOTCMD_CU                              = '339' # botCmd CU
    BOTOVR_FA                              = '340' # botOvr FA
    BOTSTF_FA                              = '341' # botStf FA
    BOTCMD_FA                              = '342' # botCmd FA
    BOTOVR_SI                              = '343' # botOvr SI
    BOTSTF_SI                              = '344' # botStf SI
    BOTCMD_SI                              = '345' # botCmd SI
    BOTOVR_SL                              = '346' # botOvr SL
    BOTSTF_SL                              = '347' # botStf SL
    BOTCMD_SL                              = '348' # botCmd SL
    BOTOVR_KC                              = '349' # botOvr KC
    BOTSTF_KC                              = '350' # botStf KC
    BOTCMD_KC                              = '351' # botCmd KC
    BOTOVR_FC                              = '352' # botOvr FC
    BOTSTF_FC                              = '353' # botStf FC
    BOTCMD_FC                              = '354' # botCmd FC
    BOTOVR_FS                              = '355' # botOvr FS
    BOTSTF_FS                              = '356' # botStf FS
    BOTCMD_FS                              = '357' # botCmd FS
    BOTOVR                                 = '358' # botOvr
    BOTSTF                                 = '359' # botStf
    BOTCMD                                 = '360' # botCmd
    BOTXRV_ONE_HUNDRED                     = '361' # botxRV100
    STF_PLUS_CH                            = '362' # Stf+ CH
    LOC_PLUS_CH                            = '363' # Loc+ CH
    PIT_PLUS_CH                            = '364' # Pit+ CH
    STF_PLUS_CU                            = '365' # Stf+ CU
    LOC_PLUS_CU                            = '366' # Loc+ CU
    PIT_PLUS_CU                            = '367' # Pit+ CU
    STF_PLUS_FA                            = '368' # Stf+ FA
    LOC_PLUS_FA                            = '369' # Loc+ FA
    PIT_PLUS_FA                            = '370' # Pit+ FA
    STF_PLUS_SI                            = '371' # Stf+ SI
    LOC_PLUS_SI                            = '372' # Loc+ SI
    PIT_PLUS_SI                            = '373' # Pit+ SI
    STF_PLUS_SL                            = '374' # Stf+ SL
    LOC_PLUS_SL                            = '375' # Loc+ SL
    PIT_PLUS_SL                            = '376' # Pit+ SL
    STF_PLUS_KC                            = '377' # Stf+ KC
    LOC_PLUS_KC                            = '378' # Loc+ KC
    PIT_PLUS_KC                            = '379' # Pit+ KC
    STF_PLUS_FC                            = '380' # Stf+ FC
    LOC_PLUS_FC                            = '381' # Loc+ FC
    PIT_PLUS_FC                            = '382' # Pit+ FC
    STF_PLUS_FS                            = '383' # Stf+ FS
    LOC_PLUS_FS                            = '384' # Loc+ FS
    PIT_PLUS_FS                            = '385' # Pit+ FS
    STUFF_PLUS                             = '386' # Stuff+
    LOCATION_PLUS                          = '387' # Location+
    PITCHING_PLUS                          = '388' # Pitching+
    STF_PLUS_FO                            = '389' # Stf+ FO
    LOC_PLUS_FO                            = '390' # Loc+ FO
    PIT_PLUS_FO                            = '391' # Pit+ FO
    QS                                     = '421' # Pit+ FO
    QUALITY_STARTS                         = QS
