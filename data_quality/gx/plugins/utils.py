import os
import ipywidgets as widgets
from datetime import date, timedelta, datetime
from data_quality.gx.plugins.metadata import METADATA

today = date.today()
start = today - timedelta(days=5)

def record_start_time():
    return datetime.now()

def extract_param_values():
    values_dict = {key_a: list(value_a.keys()) for key_a, value_a in METADATA.items()}
    run_mode_dict = {key_b: value_b['run_mode'] for value_a in METADATA.values() for key_b, value_b in value_a.items()}
    return values_dict, run_mode_dict

def calculate_execution_time(start_time):
    end_time = datetime.now()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time.total_seconds()} seconds")

ds_layer, run_mode = extract_param_values()

def initialize_widgets():
    params_to_disable = {'full': True, 'incremental': False}

    def print_params(layer, ds, mode, from_date='', to_date='', limit=''):
        os.environ["DQ_MODE"] = mode
        os.environ["DQ_LAYER"] = layer
        os.environ["DQ_DATASOURCE"] = ds
        os.environ["DQ_FROM_DATE"] = str(from_date)[:10]
        os.environ["DQ_TO_DATE"] = str(to_date)[:10]
        os.environ["DQ_LIMIT"] = str(limit)
        from_date_w.disabled = params_to_disable[os.environ["DQ_MODE"]]
        to_date_w.disabled = params_to_disable[os.environ["DQ_MODE"]]
        limit_w.disabled = params_to_disable[os.environ["DQ_MODE"]]

    def select_layer(layer):
        layer_w.options = ds_layer[layer]

    def select_mode(ds):
        mode_w.options = run_mode[ds]

    sc_w = widgets.Dropdown(options=ds_layer.keys(),
                            value = os.environ.get('DQ_LAYER', 'bronze'),
                            description='Layer:',
                            disabled=False)

    layer_w = widgets.Dropdown(options=ds_layer[sc_w.value],
                               value = os.environ.get('DQ_DATASOURCE', 'customers'),
                               row=3,
                               description='Datasource:',
                               disabled=False)

    mode_w = widgets.Dropdown(options=run_mode[layer_w.value],
                              value = os.environ.get('DQ_MODE', 'incremental'),
                              description='Run Mode:',
                              disabled=False)

    from_date_w = widgets.DatePicker(
        value=datetime.strptime(os.environ.get('DQ_FROM_DATE', str(start))[:10], '%Y-%m-%d'),
        description='From Date:',
        disabled=params_to_disable[mode_w.value]
    )

    to_date_w = widgets.DatePicker(
        value=datetime.strptime(os.environ.get('DQ_TO_DATE', str(today))[:10], '%Y-%m-%d'),
        description='To Date:',
        disabled=params_to_disable[mode_w.value]
    )

    limit_w = widgets.Text(
        value=os.environ.get('DQ_LIMIT', '1000000'),
        placeholder='1000000',
        description='Record Limit:',
        disabled=params_to_disable[mode_w.value]
    )

    widgets_combined = widgets.interactive(print_params, layer=sc_w, ds=layer_w, mode=mode_w, from_date=from_date_w,
                                           to_date=to_date_w, limit=limit_w)
    widgets_layer = widgets.interactive(select_layer, layer=sc_w)
    widgets_mode = widgets.interactive(select_mode, ds=layer_w)

    return widgets_combined
