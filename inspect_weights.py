import h5py
from pathlib import Path

h5_path = Path('models/mask_mobilenet_v2_compat.h5')


def walk_group(g, prefix=''):
    for name, item in g.items():
        full = f'{prefix}{name}'
        if isinstance(item, h5py.Dataset):
            print(f'  {full}: shape={item.shape}')
        elif isinstance(item, h5py.Group):
            walk_group(item, prefix=full + '/')

with h5py.File(h5_path, 'r') as f:
    print('Top-level weight groups:')
    for i, k in enumerate(f.keys(), start=1):
        print(f'  {i}. {k}')

    mw = f.get('model_weights') or f
    for layer_name in ['dense', 'dense_1', 'global_average_pooling2d', 'mobilenetv2_1.00_224']:
        if layer_name in mw:
            print(f'\nLayer subtree: {layer_name}')
            walk_group(mw[layer_name], prefix=layer_name + '/')

    # Try to infer number of classes from final dense/bias
    num_classes = None
    try:
        bias = mw['dense_1']['dense_1']['bias:0']
        num_classes = bias.shape[0]
    except Exception:
        pass
    if num_classes is None:
        try:
            kernel = mw['dense_1']['dense_1']['kernel:0']
            num_classes = kernel.shape[-1]
        except Exception:
            pass
    print(f"\nInferred classes from H5: {num_classes}")
