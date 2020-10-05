import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Tuple
import pandas as pd

def plot_bb_profile(df: pd.DataFrame, parameter: Optional[str] = "launch_angle") -> plt.figure:
    """Plots a given StatCast parameter split by bb_type

    Args:
        df (pd.DataFrame): StatCast pd.DataFrame (retrieved through statcast, statcast_batter, etc)
        parameter (Optional[str], optional): Parameter to plot. Defaults to "launch_angle".
    Returns:
        plt.figure: Matplotlib figure of the parameter split by bb_type 
                    (no labels, legends, etc. to allow for user customization)
    """

    bb_types = df["bb_type"].dropna().unique()
    fig = plt.figure(dpi=300)
    
    for bb_type in bb_types:
        df_skimmed = df[df.bb_type == bb_type]
        bins = np.arange(df_skimmed[parameter].min(), df_skimmed[parameter].max(), 2)
        plt.hist(df_skimmed[parameter], bins=bins, alpha=0.5, label=bb_type.replace("_"," ").capitalize())
        plt.tick_params(labelsize=12)

    return plt.gcf()
