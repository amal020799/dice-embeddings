import os
import json
import pandas as pd
import sys
import argparse


def get_default_arguments(description=None):
    parser = argparse.ArgumentParser(add_help=False)
    # Default Trainer param https://pytorch-lightning.readthedocs.io/en/stable/common/trainer.html#methods
    # Data related arguments
    parser.add_argument("--dir", type=str, default="KINSHIP-DistMult-RN/",
                        help="")
    if description is None:
        return parser.parse_args()
    return parser.parse_args(description)


# need a class to hold all params
class Experiment:
    def __init__(self):
        self.model_name = []
        self.callbacks = []
        self.embedding_dim = []
        self.num_params = []
        self.num_epochs = []
        self.batch_size = []
        self.lr = []
        self.path_dataset_folder = []
        self.full_storage_path = []
        self.pq = []
        self.train_mrr = []
        self.train_h1 = []
        self.train_h3 = []
        self.train_h10 = []

        self.val_mrr = []
        self.val_h1 = []
        self.val_h3 = []
        self.val_h10 = []

        self.test_mrr = []
        self.test_h1 = []
        self.test_h3 = []
        self.test_h10 = []

        self.runtime = []
        self.normalization = []
        self.scoring_technique = []

    def save_experiment(self, x):
        self.model_name.append(x['model'])
        self.embedding_dim.append(x['embedding_dim'])
        self.num_epochs.append(x['num_epochs'])
        self.batch_size.append(x['batch_size'])
        self.lr.append(x['lr'])
        self.path_dataset_folder.append(x['path_dataset_folder'])
        self.pq.append((x['p'], x['q']))
        self.runtime.append(x['Runtime'])
        self.num_params.append(x['NumParam'])

        self.normalization.append(x['normalization'])
        self.scoring_technique.append(x['scoring_technique'])
        self.callbacks.append(x['callbacks'])

        self.train_mrr.append(x['Train']['MRR'])
        self.train_h1.append(x['Train']['H@1'])
        self.train_h3.append(x['Train']['H@3'])
        self.train_h10.append(x['Train']['H@10'])

        # Partition by delim and take the last one
        self.full_storage_path.append(x['full_storage_path'].partition('dice-embeddings')[-1])

        self.val_mrr.append(x['Val']['MRR'])
        self.val_h1.append(x['Val']['H@1'])
        self.val_h3.append(x['Val']['H@3'])
        self.val_h10.append(x['Val']['H@10'])

        self.test_mrr.append(x['Test']['MRR'])
        self.test_h1.append(x['Test']['H@1'])
        self.test_h3.append(x['Test']['H@3'])
        self.test_h10.append(x['Test']['H@10'])

    def to_df(self):
        return pd.DataFrame(
            dict(model_name=self.model_name,  # pq=self.pq, path_dataset_folder=self.path_dataset_folder,
                 train_mrr=self.train_mrr, train_h1=self.train_h1,
                 train_h3=self.train_h3, train_h10=self.train_h10,
                 # full_storage_path=self.full_storage_path,
                 val_mrr=self.val_mrr, val_h1=self.val_h1,
                 val_h3=self.val_h3, val_h10=self.val_h10,
                 test_mrr=self.test_mrr, test_h1=self.test_h1,
                 test_h3=self.test_h3, test_h10=self.test_h10,
                 runtime=self.runtime,
                 params=self.num_params,
                 callbacks=self.callbacks,
                 # normalization=self.normalization,
                 # embeddingdim=self.embedding_dim
                 scoring_technique=self.scoring_technique
                 )
        )


def analyse(args):
    # (2) Get all subfolders
    sub_folder_str_paths = os.listdir(args.dir)
    experiments = []
    for path in sub_folder_str_paths:
        full_path=args.dir +"/"+path
        with open(f'{full_path}/configuration.json', 'r') as f:
            config = json.load(f)
            config = {i: config[i] for i in
                      ['model', 'full_storage_path', 'embedding_dim',
                       'normalization', 'num_epochs', 'batch_size', 'lr',
                       'callbacks',
                       'scoring_technique',
                       "scoring_technique",
                       'path_dataset_folder', 'p', 'q']}
        with open(f'{full_path}/report.json', 'r') as f:
            report = json.load(f)
            report = {i: report[i] for i in ['Runtime', 'NumParam']}
        with open(f'{full_path}/eval_report.json', 'r') as f:
            eval_report = json.load(f)

        config.update(eval_report)
        config.update(report)
        experiments.append(config)

    counter = Experiment()

    for i in experiments:
        counter.save_experiment(i)

    df = counter.to_df()
    df.sort_values(by=['test_mrr'], ascending=False, inplace=True)
    pd.set_option("display.precision", 3)
    # print(df)
    print(df.to_latex(index=False, float_format="%.3f"))
    #print(df.to_markdown(index=False))
    df.to_csv(path_or_buf=args.dir+'/summary.csv')


if __name__ == '__main__':
    analyse(get_default_arguments())
