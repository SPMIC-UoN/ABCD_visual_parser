import dash
import pandas as pd
import numpy as np
import itertools
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, MATCH
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from collections import defaultdict

from psych_dashboard.app import app, all_manhattan_components, default_marker_color
from psych_dashboard.load_feather import load_flattened_logs, load_logs, load_pval, load_filtered_feather


# TODO: currently only allows int64 and float64
valid_manhattan_dtypes = [np.int64, np.float64]


@app.callback(
    [Output({'type': 'div_manhattan_' + str(t), 'index': MATCH}, 'children')
     for t in [component['id'] for component in all_manhattan_components]],
    [Input('df-loaded-div', 'children')],
    [State({'type': 'manhattan_' + component['id'], 'index': MATCH}, prop)
     for component in all_manhattan_components for prop in component]
)
def select_manhattan_variables(df_loaded, *args):
    print('select_manhattan_variables', *args)
    # Generate the list of argument names based on the input order
    keys = [(component['id'], str(prop))
            for component in all_manhattan_components for prop in component]
    print(keys)
    args_dict = defaultdict(dict)
    for key, value in zip(keys, args):
        # if key[0] not in new_args_dict:
        #     new_args_dict[key[0]] = dict()
        args_dict[key[0]][key[1]] = value

    print('args_dict', args_dict)
    # Convert inputs to a dict called 'args_dict'
    # args_dict = dict(zip(keys, args))
    # print('man args_dict', args_dict)
    dff = load_pval()
    dd_options = [{'label': col,
                   'value': col} for col in dff.columns if dff[col].dtype in valid_manhattan_dtypes]

    children = list()
    for component in all_manhattan_components:
        name = component['id'] # 'base_variable'
        if component['component_type'] == 'Dropdown':
            print(component, 'Dropdown')
            print('args_dict1', args_dict)
            other_args = dict(args_dict[name])
            del other_args['id']
            del other_args['component_type']
            del other_args['label']
            del other_args['options']
            print('other_args', other_args)
            print('args_dict2', args_dict)
            print(args_dict[component['id']])
            print(args_dict[name])
            children.append([component['label'] + ":",
                             dcc.Dropdown(id={'type': 'manhattan_' + name, 'index': args_dict[name]['id']['index']},
                                          options=dd_options,
                                          **other_args
                                          )],
                            )
        elif component['component_type'] == 'Input':
            print(component, 'Input')
            other_args = dict(args_dict[name])
            del other_args['id']
            del other_args['component_type']
            del other_args['label']
            children.append([component['label'] + ":",
                             dcc.Input(id={'type': 'manhattan_' + name, 'index': args_dict[name]['id']['index']},
                                       **other_args,
                                       )],
                            )
        elif component['component_type'] == 'Checklist':
            print(component, 'Checklist')
            other_args = dict(args_dict[name])
            del other_args['id']
            del other_args['component_type']
            del other_args['label']
            children.append([component['label'] + ":",
                             dcc.Checklist(id={'type': 'manhattan_' + name, 'index': args_dict[name]['id']['index']},
                                           **other_args
                                           )],
                            )
    return children

    # return tuple([[dd_manhattan_dims[dim] + ":",
    #                dcc.Dropdown(id={'type': 'manhattan_'+dim, 'index': args_dict[dim]['index']},
    #                             options=dd_options,
    #                             value=args_dict[dim+'_val'])
    #                ] for dim in dd_manhattan_dims.keys()] +
    #              [[input_manhattan_dims[dim] + ":",
    #                dcc.Input(id={'type': 'manhattan_'+dim, 'index': args_dict[dim]['index']},
    #                          type='number',
    #                          min=0,
    #                          step=0.001,
    #                          value=args_dict[dim+'_val'])
    #                ] for dim in input_manhattan_dims.keys()] +
    #              [[check_manhattan_dims[dim] + ":",
    #                dcc.Checklist(id={'type': 'manhattan_'+dim, 'index': args_dict[dim]['index']},
    #                              options=[{'label': '', 'value': 'LOG'}],
    #                              value=args_dict[dim+'_val'])
    #                ] for dim in check_manhattan_dims.keys()]
    #              )


def calculate_transformed_corrected_pval(ref_pval, logs):
    # Divide reference p-value by number of variable pairs to get corrected p-value
    corrected_ref_pval = ref_pval / (logs.notna().sum().sum())
    # Transform corrected p-value by -log10
    transformed_corrected_ref_pval = -np.log10(corrected_ref_pval)
    return transformed_corrected_ref_pval


def calculate_manhattan_data(dff, manhattan_variable):
    # Filter columns to those with valid types.

    if manhattan_variable is None:
        manhattan_variables = dff.columns
    else:
        if isinstance(manhattan_variable, list):
            manhattan_variables = manhattan_variable
        else:
            manhattan_variables = [manhattan_variable]

    # Create DF to hold the results of the calculations, and perform the log calculation
    logs = pd.DataFrame(columns=dff.columns, index=manhattan_variables)
    for variable in dff:
        logs[variable] = -np.log10(dff[variable])

    # Now blank out any duplicates including the diagonal
    for ind in logs.index:
        for col in logs.columns:
            if ind in logs.columns and col in logs.index and logs[col][ind] == logs[ind][col]:
                logs[ind][col] = np.nan

    return logs


def flattened(df):
    """
    Convert a DF into a Series, where the MultiIndex of each element is a combination of the index/col from the original DF
    :param df:
    :return:
    """
    s = pd.Series(index=pd.MultiIndex.from_tuples(itertools.product(df.index, df.columns), names=['first', 'second']), name='value')
    for (a, b) in itertools.product(df.index, df.columns):
        s[a, b] = df[b][a]
    return s


@app.callback(
    Output({'type': 'gen_manhattan_graph', 'index': MATCH}, "figure"),
    [*(Input({'type': 'manhattan_' + d, 'index': MATCH}, "value") for d in [component['id'] for component in all_manhattan_components])],
)
def make_manhattan_figure(*args):
    print('make_manhattan_figure', *args)
    # [State({'type': 'manhattan_' + component['name'], 'index': MATCH}, prop)
    #  for component in all_manhattan_components for prop in component]
    keys = [str([component['id'] for component in all_manhattan_components][i]) for i in range(0, int(len(args)))]
    print(keys)
    args_dict = dict(zip(keys, args))
    print(args_dict)
    if args_dict['base_variable'] is None or args_dict['base_variable'] == []:
        print('return go.Figure()')
        raise PreventUpdate

    if args_dict['pvalue'] is None or args_dict['pvalue'] <= 0.:
        print('raise PreventUpdate')
        raise PreventUpdate

    ctx = dash.callback_context
    print('ctx triggered', ctx.triggered[0]['prop_id'])
    # Calculate p-value of corr coeff per variable against the manhattan variable, and the significance threshold.
    # Save logs and flattened logs to feather files
    # Skip this and reuse the previous values if we're just changing the log scale.
    if ctx.triggered[0]['prop_id'] not in ['manhattan-logscale-check.value', 'manhattan-pval-input.value']:
        logs = calculate_manhattan_data(load_pval(), args_dict['base_variable'])
        logs.reset_index().to_feather('logs.feather')
        flattened_logs = flattened(logs).dropna()
        flattened_logs.reset_index().to_feather('flattened_logs.feather')
        transformed_corrected_ref_pval = calculate_transformed_corrected_pval(float(args_dict['pvalue']), logs)
    else:
        print('using logscale shortcut')
        logs = load_logs()
        flattened_logs = load_flattened_logs()
        transformed_corrected_ref_pval = calculate_transformed_corrected_pval(float(args_dict['pvalue']), logs)

    fig = go.Figure(go.Scatter(x=[[item[i] for item in flattened_logs.index[::-1]] for i in range(0, 2)],
                               y=np.flip(flattened_logs.values),
                               mode='markers'
                               ),
                    )

    fig.update_layout(shapes=[
        dict(
            type='line',
            yref='y', y0=transformed_corrected_ref_pval, y1=transformed_corrected_ref_pval,
            xref='x', x0=0, x1=len(flattened_logs)-1
        )
    ],
        annotations=[
            dict(
                x=0,
                y=transformed_corrected_ref_pval if args_dict['logscale'] != ['LOG'] else np.log10(transformed_corrected_ref_pval),
                xref='x',
                yref='y',
                text='{:f}'.format(transformed_corrected_ref_pval),
                showarrow=True,
                arrowhead=7,
                ax=-50,
                ay=0
            ),
            ],
        xaxis_title='variable',
        yaxis_title='-log10(p)',
        yaxis_type='log' if args_dict['logscale'] == ['LOG'] else None
    )
    return fig