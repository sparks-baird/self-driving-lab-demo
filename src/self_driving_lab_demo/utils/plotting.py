from typing import Union

import plotly.express as px
import plotly.graph_objs as go


def line(error_y_mode=None, **kwargs):
    """Extension of `plotly.express.line` to use error bands.

    Source: https://stackoverflow.com/a/69587615/13697228

    Example
    -------
    >>> import plotly.express as px
    >>> import pandas
    >>>
    >>> df = px.data.gapminder().query('continent=="Americas"')
    >>> df = df[df['country'].isin({'Argentina','Brazil','Colombia'})]
    >>> df['lifeExp std'] = df['lifeExp']*.1 # Invent some error data...
    >>>
    >>> for error_y_mode in {'band', 'bar'}:
    >>>     fig = line(
    >>>         data_frame = df,
    >>>         x = 'year',
    >>>         y = 'lifeExp',
    >>>         error_y = 'lifeExp std',
    >>>         error_y_mode = error_y_mode,
    >>>         color = 'country',
    >>>         title = f'Using error {error_y_mode}',
    >>>         markers = '.',
    >>>     )
    >>>     fig.show()
    """
    ERROR_MODES = {"bar", "band", "bars", "bands", None}
    if error_y_mode not in ERROR_MODES:
        raise ValueError(
            f"'error_y_mode' must be one of {ERROR_MODES}, received {repr(error_y_mode)}."  # noqa: E501
        )
    if error_y_mode in {"bar", "bars", None}:
        fig = px.line(**kwargs)
    elif error_y_mode in {"band", "bands"}:
        if "error_y" not in kwargs:
            raise ValueError(
                "Argument 'error_y_mode' must come with 'error_y' provided."
            )
        figure_with_error_bars = px.line(**kwargs)
        fig = px.line(**{arg: val for arg, val in kwargs.items() if arg != "error_y"})
        for data in figure_with_error_bars.data:
            x = list(data["x"])
            y_upper = list(data["y"] + data["error_y"]["array"])
            y_lower = list(
                data["y"] - data["error_y"]["array"]
                if data["error_y"]["arrayminus"] is None
                else data["y"] - data["error_y"]["arrayminus"]
            )
            color = (
                f"rgba({tuple(int(data['line']['color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))},.3)".replace(  # noqa: E501
                    "((", "("
                )
                .replace("),", ",")
                .replace(" ", "")
            )
            fig.add_trace(
                go.Scatter(
                    x=x + x[::-1],
                    y=y_upper + y_lower[::-1],
                    fill="toself",
                    fillcolor=color,
                    line=dict(color="rgba(255,255,255,0)"),
                    hoverinfo="skip",
                    showlegend=False,
                    legendgroup=data["legendgroup"],
                    xaxis=data["xaxis"],
                    yaxis=data["yaxis"],
                )
            )
        # Reorder data as said here: https://stackoverflow.com/a/66854398/8849755
        reordered_data = []
        for i in range(int(len(fig.data) / 2)):
            reordered_data.append(fig.data[i + int(len(fig.data) / 2)])
            reordered_data.append(fig.data[i])
        fig.data = tuple(reordered_data)
    return fig


def matplotlibify(
    fig: go.Figure,
    size: int = 24,
    width_inches: Union[float, int] = 3.5,
    height_inches: Union[float, int] = 3.5,
    dpi: int = 142,
    return_scale: bool = False,
) -> go.Figure:
    """Make plotly figures look more like matplotlib for academic publishing.

    modified from: https://medium.com/swlh/fa56ddd97539

    Parameters
    ----------
    fig : go.Figure
        Plotly figure to be matplotlibified
    size : int, optional
        Font size for layout and axes, by default 24
    width_inches : Union[float, int], optional
        Width of matplotlib figure in inches, by default 3.5
    height_inches : Union[float, int], optional
        Height of matplotlib figure in Inches, by default 3.5
    dpi : int, optional
        Dots per inch (resolution) of matplotlib figure, by default 142. Leave as
        default unless you're willing to verify nothing strange happens with the output.
    return_scale : bool, optional
        If true, then return `scale` which is a quantity that helps with creating a
        high-resolution image at the specified absolute width and height in inches.
        More specifically:
        >>> width_default_px = fig.layout.width
        >>> targ_dpi = 300
        >>> scale = width_inches / (width_default_px / dpi) * (targ_dpi / dpi)
        Feel free to ignore this parameter.

    Returns
    -------
    fig : go.Figure
        The matplotlibified plotly figure.

    Examples
    --------
    >>> import plotly.express as px
    >>> df = px.data.tips()
    >>> fig = px.histogram(df, x="day")
    >>> fig.show()
    >>> fig = matplotlibify(fig, size=24, width_inches=3.5, height_inches=3.5, dpi=142)
    >>> fig.show()

    Note the difference between
    https://user-images.githubusercontent.com/45469701/171044741-35591a2c-dede-4df1-ae47-597bbfdb89cf.png # noqa: E501
    and
    https://user-images.githubusercontent.com/45469701/171044746-84a0deb0-1e15-40bf-a459-a5a7d3425b20.png, # noqa: E501
    which are both static exports of interactive plotly figures.
    """
    font_dict = dict(family="Arial", size=size, color="black")

    # app = QApplication(sys.argv)
    # screen = app.screens()[0]
    # dpi = screen.physicalDotsPerInch()
    # app.quit()

    fig.update_layout(
        font=font_dict,
        plot_bgcolor="white",
        width=width_inches * dpi,
        height=height_inches * dpi,
        margin=dict(r=40, t=20, b=10),
    )

    fig.update_yaxes(
        showline=True,  # add line at x=0
        linecolor="black",  # line color
        linewidth=2.4,  # line size
        ticks="inside",  # ticks outside axis
        tickfont=font_dict,  # tick label font
        mirror="allticks",  # add ticks to top/right axes
        tickwidth=2.4,  # tick width
        tickcolor="black",  # tick color
    )

    fig.update_xaxes(
        showline=True,
        showticklabels=True,
        linecolor="black",
        linewidth=2.4,
        ticks="inside",
        tickfont=font_dict,
        mirror="allticks",
        tickwidth=2.4,
        tickcolor="black",
    )
    fig.update(layout_coloraxis_showscale=False)

    width_default_px = fig.layout.width
    targ_dpi = 300
    scale = width_inches / (width_default_px / dpi) * (targ_dpi / dpi)

    if return_scale:
        return fig, scale
    else:
        return fig


def plot_and_save(fig_path, fig, mpl_kwargs={}, show=False, update_legend=False):
    if show:
        fig.show()
    fig.write_html(fig_path + ".html")
    fig.to_json(fig_path + ".json")
    if update_legend:
        fig.update_layout(
            legend=dict(
                font=dict(size=16),
                yanchor="bottom",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(0,0,0,0)",
                # orientation="h",
            )
        )
    fig = matplotlibify(fig, **mpl_kwargs)
    fig.write_image(fig_path + ".png")
