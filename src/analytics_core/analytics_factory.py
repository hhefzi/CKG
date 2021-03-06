from analytics_core.analytics import wgcnaAnalysis as wgcna
from analytics_core.analytics import analytics
from analytics_core.viz import viz
import pandas as pd
import itertools
import time


class Analysis:
    def __init__(self, identifier, analysis_type, args, data, result=None):
        self._identifier = identifier
        self._analysis_type = analysis_type
        self._args = args
        self._data = data
        self._result = result
        if self._result is None:
            self._result = {}
            self.generate_result()

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, identifier):
        self._identifier = identifier

    @property
    def analysis_type(self):
        return self._analysis_type

    @analysis_type.setter
    def analysis_type(self, analysis_type):
        self._analysis_type = analysis_type

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, args):
        self._args = args

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result):
        self._result = result

    def generate_result(self):
        if self.analysis_type == "wide_format":
            r = analytics.transform_into_wide_format(self.data, self.args['index'], self.args['columns'], self.args['values'], extra=[self.args['extra']])
            self.result[self.analysis_type] = r
        if self.analysis_type == "summary":
            value_cols = None
            r = analytics.get_summary_data_matrix(self.data)
            self.result[self.analysis_type] = r
        if self.analysis_type == "normalization":
            method = 'median_polish'
            if 'method' in self.args:
                method = self.args['method']
            self.result[self.analysis_type] = analytics.normalize_data(self.data, method=method)
        if self.analysis_type == "pca":
            components = 2
            drop_cols = []
            if "components" in self.args:
                components = self.args["components"]
            if "drop_cols" in self.args:
                drop_cols = self.args["drop_cols"]
            self.result, nargs = analytics.run_pca(self.data, components=components, drop_cols=drop_cols)
            self.args.update(nargs)
        elif self.analysis_type == "tsne":
            components = 2
            perplexity = 40
            n_iter = 1000
            drop_cols = []
            init = 'pca'
            if "components" in self.args:
                components = self.args["components"]
            if "perplexity" in self.args:
                perplexity = self.args["perplexity"]
            if "n_iter" in self.args:
                n_iter = self.args["n_iter"]
            if "init" in self.args:
                init = self.args["init"]
            if "drop_cols" in self.args:
                drop_cols = self.args["drop_cols"]
            self.result, nargs = analytics.run_tsne(self.data, components=components, drop_cols=drop_cols, perplexity=perplexity, n_iter=n_iter, init=init)
            self.args.update(nargs)
        elif self.analysis_type == "umap":
            n_neighbors = 10
            min_dist = 0.3
            metric = 'cosine'
            if "n_neighbors" in self.args:
                n_neighbors = self.args["n_neighbors"]
            if "min_dist" in self.args:
                min_dist = self.args["min_dist"]
            if "metric" in self.args:
                metric = self.args["metric"]
            if n_neighbors < self.data.shape[0]:
                self.result, nargs = analytics.run_umap(self.data, n_neighbors=n_neighbors, min_dist=min_dist, metric=metric)
                self.args.update(nargs)
        elif self.analysis_type == "mapper":
            n_cubes = 15
            overlap = 0.5
            n_clusters = 3
            linkage = "complete"
            affinity = "correlation"
            labels = {}
            if "labels" in self.args:
                labels = self.args["labels"]
            if "n_cubes" in self.args:
                n_cubes = self.args["n_cubes"]
            if "overlap" in self.args:
                overlap = self.args["overlap"]
            if "n_clusters" in self.args:
                n_clusters = self.args["n_clusters"]
            if "linkage" in self.args:
                linkage = self.args["linkage"]
            if "affinity" in self.args:
                affinity = self.args["affinity"]
            r, nargs = analytics.run_mapper(self.data, n_cubes=n_cubes, overlap=overlap, n_clusters=n_clusters, linkage=linkage, affinity=affinity)
            self.args.update(nargs)
            self.result[self.analysis_type] = r
        elif self.analysis_type == 'ttest':
            alpha = 0.05
            correction = 'fdr_bh'
            if "alpha" in self.args:
                alpha = self.args["alpha"]
            if 'correction_method' in self.args:
                correction = self.args['correction_method']
            for pair in itertools.combinations(self.data.group.unique(), 2):
                ttest_result = analytics.run_ttest(self.data, pair[0], pair[1], alpha=0.05, correction=correction)
                self.result[pair] = ttest_result
        elif self.analysis_type == 'anova':
            start = time.time()
            alpha = 0.05
            drop_cols = []
            group = 'group'
            subject = 'subject'
            permutations = 50
            is_logged = True
            correction = 'fdr_bh'
            if "alpha" in self.args:
                alpha = self.args["alpha"]
            if "drop_cols" in self.args:
                drop_cols = self.args['drop_cols']
            if "subject" in self.args:
                subject = self.args['subject']
            if "group" in self.args:
                group = self.args["group"]
            if "permutations" in self.args:
                permutations = self.args["permutations"]
            if "is_logged" in self.args:
                is_logged = self.args['is_logged']
            if 'correction_method' in self.args:
                correction = self.args['correction_method']
            anova_result = analytics.run_anova(self.data, drop_cols=drop_cols, subject=subject, group=group, alpha=alpha, permutations=permutations, is_logged=is_logged, correction=correction)
            self.result[self.analysis_type] = anova_result
        elif self.analysis_type == 'qcmarkers':
            sample_col = 'sample'
            group_col = 'group'
            identifier_col = 'identifier'
            qcidentifier_col = 'identifier'
            qcclass_col = 'class'
            drop_cols = ['subject']
            if 'drop_cols' in self.args:
                drop_cols = self.args['drop_cols']
            if 'sample_col' in self.args:
                sample_col = self.args['sample_col']
            if 'group_col' in self.args:
                group_col = self.args['group_col']
            if 'identifier_col' in self.args:
                identifier_col = self.args['identifier_col']
            if 'qcidentifier_col' in self.args:
                qcidentifier_col = self.args['qcidentifier_col']
            if 'qcclass_col' in self.args:
                qcclass_col = self.args['qcclass_col']
            if 'processed' in self.data and 'tissue qcmarkers' in self.data:
                processed_data = self.data['processed']
                qcmarkers = self.data['tissue qcmarkers']
                self.result[self.analysis_type] = analytics.run_qc_markers_analysis(processed_data, qcmarkers, sample_col, group_col, drop_cols, identifier_col, qcidentifier_col, qcclass_col)
        elif self.analysis_type == 'samr':
            start = time.time()
            alpha = 0.05
            s0 = None
            drop_cols = []
            group = 'group'
            subject = 'subject'
            permutations = 250
            fc = 0
            is_logged = True
            if "alpha" in self.args:
                alpha = self.args["alpha"]
            if "drop_cols" in self.args:
                drop_cols = self.args['drop_cols']
            if "subject" in self.args:
                subject = self.args['subject']
            if "group" in self.args:
                group = self.args["group"]
            if "s0" in self.args:
                s0 = self.args["s0"]
            if "permutations" in self.args:
                permutations = self.args["permutations"]
            if "fc" in self.args:
                fc = self.args['fc']
            if "is_logged" in self.args:
                is_logged = self.args['is_logged']
            anova_result = analytics.run_samr(self.data, drop_cols=drop_cols, subject=subject, group=group, alpha=alpha, s0=s0, permutations=permutations, fc=fc, is_logged=is_logged)
            self.result[self.analysis_type] = anova_result
        elif self.analysis_type == '2-way anova':
            drop_cols = []
            subject = 'subject'
            group = ['group', 'secondary_group']
            if "drop_cols" in self.args:
                drop_cols = self.args['drop_cols']
            if "subject" in self.args:
                subject = self.args["subject"]
            if "group" in self.args:
                group = self.args["group"]
            two_way_anova_result = analytics.run_two_way_anova(self.data, drop_cols=drop_cols, subject=subject, group=group)
            self.result[self.analysis_type] = two_way_anova_result
        elif self.analysis_type == "repeated_measurements_anova":
            start = time.time()
            alpha = 0.05
            drop_cols = []
            group = 'group'
            subject = 'subject'
            permutations = 50
            correction = 'fdr_bh'
            if "alpha" in self.args:
                alpha = self.args["alpha"]
            if "drop_cols" in self.args:
                drop_cols = self.args['drop_cols']
            if "group" in self.args:
                group = self.args["group"]
            if "subject" in self.args:
                subject = self.args["subject"]
            if "permutations" in self.args:
                permutations = self.args["permutations"]
            if 'correction_method' in self.args:
                correction = self.args['correction_method']
            anova_result = analytics.run_repeated_measurements_anova(self.data, drop_cols=drop_cols, subject=subject, group=group, alpha=alpha, permutations=permutations, correction=correction)
            self.result[self.analysis_type] = anova_result
            print('repeated-ANOVA', time.time() - start)
        elif self.analysis_type == "dabest":
            drop_cols = []
            group = 'group'
            subject = 'subject'
            test = 'mean_diff'
            if "drop_cols" in self.args:
                drop_cols = self.args['drop_cols']
            if "group" in self.args:
                group = self.args["group"]
            if "subject" in self.args:
                subject = self.args["subject"]
            if "test" in self.args:
                test = self.args["test"]
            dabest_result = analytics.run_dabest(self.data, drop_cols=drop_cols, subject=subject, group=group, test=test)
            self.result[self.analysis_type] = dabest_result
        elif self.analysis_type == "correlation":
            start = time.time()
            alpha = 0.05
            method = 'pearson'
            correction = 'fdr_bh'
            subject = 'subject'
            group = 'group'
            if 'group' in self.args:
                group = self.args['group']
            if 'subject' in self.args:
                subject = self.args['subject']
            if "alpha" in self.args:
                alpha = self.args["args"]
            if "method" in self.args:
                method = self.args["method"]
            if "correction" in self.args:
                correction = self.args["correction"]
            self.result[self.analysis_type] = analytics.run_correlation(self.data, alpha=alpha, subject=subject, group=group, method=method, correction=correction)
        elif self.analysis_type == "repeated_measurements_correlation":
            start = time.time()
            alpha = 0.05
            method = 'pearson'
            correction = 'fdr_bh'
            cutoff = 0.5
            subject = 'subject'
            if 'subject' in self.args:
                subject = self.args['subject']
            if "alpha" in self.args:
                alpha = self.args["args"]
            if "method" in self.args:
                method = self.args["method"]
            if "correction" in self.args:
                correction = self.args["correction"]
            self.result[self.analysis_type] = analytics.run_rm_correlation(self.data, alpha=alpha, subject=subject, correction=correction)
        elif self.analysis_type == "merge_for_polar":
            theta_col = 'modifier'
            group_col = 'group'
            identifier_col = 'identifier'
            normalize = True
            aggr_func = 'mean'
            if 'group_col' in self.args:
                group_col = self.args['group_col']
            if 'theta_col' in self.args:
                theta_col = self.args['theta_col']
            if 'identifier_col' in self.args:
                identifier_col = self.args['identifier_col']
            if 'aggr_func' in self.args:
                aggr_func = self.args['aggr_func']
            if 'normalize' in self.args:
                normalize = self.args['normalize']
            if 'regulation_data' in self.args and 'regulators' in self.args:
                if self.args['regulation_data'] in self.data and self.args['regulators'] in self.data:
                    self.result[self.analysis_type] = analytics.merge_for_polar(self.data[self.args['regulation_data']], self.data[self.args['regulators']], identifier_col=identifier_col, group_col=group_col, theta_col=theta_col, aggr_func=aggr_func, normalize=normalize)
        elif self.analysis_type == "regulation_enrichment":
            start = time.time()
            identifier = 'identifier'
            groups = ['group1', 'group2']
            annotation_col = 'annotation'
            reject_col = 'rejected'
            method = 'fisher'
            annotation_type = 'functional'
            correction = 'fdr_bh'
            if 'identifier' in self.args:
                identifier = self.args['identifier']
            if 'groups' in self.args:
                groups = self.args['groups']
            if 'annotation_col' in self.args:
                annotation_col = self.args['annotation_col']
            if 'reject_col' in self.args:
                reject_col = self.args['reject_col']
            if 'method' in self.args:
                method = self.args['method']
            if 'annotation_type' in self.args:
                annotation_type = self.args['annotation_type']
            if 'correction_method' in self.args:
                correction = self.args['correction_method']
            if 'regulation_data' in self.args and 'annotation' in self.args:
                if self.args['regulation_data'] in self.data and self.args['annotation'] in self.data:
                    self.analysis_type = annotation_type+"_"+self.analysis_type
                    self.result[self.analysis_type] = analytics.run_regulation_enrichment(self.data[self.args['regulation_data']], self.data[self.args['annotation']], 
                                                                                          identifier=identifier, groups=groups, annotation_col=annotation_col, reject_col=reject_col, 
                                                                                          method=method, correction=correction)
            print('Enrichment', time.time() - start)
        elif self.analysis_type == "regulation_site_enrichment":
            start = time.time()
            identifier = 'identifier'
            groups = ['group1', 'group2']
            annotation_col = 'annotation'
            reject_col = 'rejected'
            method = 'fisher'
            annotation_type = 'functional'
            regex = "(\w+~.+)_\w\d+\-\w+"
            correction = 'fdr_bh'
            if 'identifier' in self.args:
                identifier = self.args['identifier']
            if 'groups' in self.args:
                groups = self.args['groups']
            if 'annotation_col' in self.args:
                annotation_col = self.args['annotation_col']
            if 'reject_col' in self.args:
                reject_col = self.args['reject_col']
            if 'method' in self.args:
                method = self.args['method']
            if 'annotation_type' in self.args:
                annotation_type = self.args['annotation_type']
            if 'regex' in self.args:
                regex = self.args['regex']
            if 'correction_method' in self.args:
                correction = self.args['correction_method']
            if 'regulation_data' in self.args and 'annotation' in self.args:
                if self.args['regulation_data'] in self.data and self.args['annotation'] in self.data:
                    self.analysis_type = annotation_type+"_"+self.analysis_type
                    self.result[self.analysis_type] = analytics.run_site_regulation_enrichment(self.data[self.args['regulation_data']],
                                                                                               self.data[self.args['annotation']], identifier=identifier,
                                                                                               groups=groups, annotation_col=annotation_col, reject_col=reject_col,
                                                                                               method=method, regex=regex, correction=correction)
        elif self.analysis_type == 'long_format':
            self.result[self.analysis_type] = analytics.transform_into_long_format(self.data, drop_columns=self.args['drop_columns'], group=self.args['group'], columns=self.args['columns'])
        elif self.analysis_type == 'ranking_with_markers':
            start = time.time()
            list_markers = []
            annotations = {}
            marker_col = 'identifier'
            marker_of_col = 'disease'
            if 'identifier' in self.args:
                marker_col = self.args['identifier']
            if 'marker_of' in self.args:
                marker_of_col = self.args['marker_of']
            if 'markers' in self.args:
                if self.args['markers'] in self.data:
                    if marker_col in self.data[self.args['markers']]:
                        list_markers = self.data[self.args['markers']][marker_col].tolist()
                        if 'annotate' in self.args:
                            if self.args['annotate']:
                                annotations = pd.Series(self.data[self.args['markers']][marker_of_col].values, index=self.data[self.args['markers']][marker_col]).to_dict()
            self.args['annotations'] = annotations
            if 'data' in self.args:
                if self.args['data'] in self.data:
                    self.result[self.analysis_type] = analytics.get_ranking_with_markers(self.data[self.args['data']], drop_columns=self.args['drop_columns'], group=self.args['group'], columns=self.args['columns'], list_markers=list_markers, annotation = annotations)
        elif self.analysis_type == 'coefficient_of_variation':
            self.result[self.analysis_type] = analytics.get_coefficient_variation(self.data, drop_columns=self.args['drop_columns'], group=self.args['group'], columns=self.args['columns'])
        elif self.analysis_type == 'publications_abstracts':
            self.result[self.analysis_type] = analytics.get_publications_abstracts(self.data, publication_col="publication", join_by=['publication', 'Proteins'], index="PMID")
        elif self.analysis_type == "wgcna":
            start = time.time()
            drop_cols_exp = []
            drop_cols_cli = []
            RsquaredCut = 0.8
            networkType = 'unsigned'
            minModuleSize = 30
            deepSplit = 2
            pamRespectsDendro = False
            merge_modules = True
            MEDissThres = 0.25
            verbose = 0
            sd_cutoff = 0
            if "drop_cols_exp" in self.args:
                drop_cols_exp = self.args['drop_cols_exp']
            if "drop_cols_cli" in self.args:
                drop_cols_cli = self.args['drop_cols_cli']
            if "RsquaredCut" in self.args:
                RsquaredCut = self.args["RsquaredCut"]
            if "networkType" in self.args:
                networkType = self.args["networkType"]
            if "minModuleSize" in self.args:
                minModuleSize = self.args["minModuleSize"]
            if "deepSplit" in self.args:
                deepSplit = self.args["deepSplit"]
            if "pamRespectsDendro" in self.args:
                pamRespectsDendro = self.args["pamRespectsDendro"]
            if "merge_modules" in self.args:
                merge_modules = self.args["merge_modules"]
            if "MEDissThres" in self.args:
                MEDissThres = self.args["MEDissThres"]
            if "verbose" in self.args:
                verbose = self.args["verbose"]
            if "sd_cutoff" in self.args:
                sd_cutoff = self.args["sd_cutoff"]
            self.result[self.analysis_type] = analytics.run_WGCNA(self.data, drop_cols_exp, drop_cols_cli, RsquaredCut=RsquaredCut, networkType=networkType, 
                                                            minModuleSize=minModuleSize, deepSplit=deepSplit, pamRespectsDendro=pamRespectsDendro, merge_modules=merge_modules,
                                                            MEDissThres=MEDissThres, verbose=verbose, sd_cutoff=sd_cutoff)
        elif self.analysis_type == 'kaplan_meier':
            time_col = None
            event_col = None
            group_col = 'group'
            if 'time_col' in self.args:
                time_col = self.args['time_col']
            if 'event_col' in self.args:
                event_col = self.args['event_col']
            if 'group_col' in self.args:
                group_col = self.args['group_col']
            self.result[self.analysis_type] = analytics.run_km(self.data, time_col, event_col, group_col, self.args)
        elif self.analysis_type == 'multi_correlation':
            start = time.time()
            alpha = 0.05
            method = 'pearson'
            correction = 'fdr_bh'
            subject = 'subject'
            group = 'group'
            on = ['subject', 'group']
            if 'on_cols' in self.args:
                on = self.args['on_cols']
            if 'group' in self.args:
                group = self.args['group']
            if 'subject' in self.args:
                subject = self.args['subject']
            if "alpha" in self.args:
                alpha = self.args["args"]
            if "method" in self.args:
                method = self.args["method"]
            if "correction" in self.args:
                correction = self.args["correction"]
            self.result[self.analysis_type] = analytics.run_multi_correlation(self.data, alpha=alpha, subject=subject, group=group, on=on, method=method, correction=correction)

    def get_plot(self, name, identifier):
        plot = []
        if len(self.result) >= 1:
            if name == "basicTable":
                colors = ('#C2D4FF', '#F5F8FF')
                attr = {'width': 800, 'height': 1500, 'font': 12}
                subset = None
                figure_title = 'Basic table'
                if "colors" in self.args:
                    colors = self.args["colors"]
                if "attr" in self.args:
                    attr = self.args["attr"]
                if "subset" in self.args:
                    subset = self.args["subset"]
                if "title" in self.args:
                    figure_title = self.args["title"]
                for id in self.result:
                    if isinstance(id, tuple):
                        identifier = identifier+"_"+id[0]+"_vs_"+id[1]
                        figure_title = self.args["title"] + id[0]+" vs "+id[1]
                    plot.append(viz.get_table(self.result[id], identifier, figure_title, colors=colors, subset=subset, plot_attr=attr))
            if name == "multiTable":
                for id in self.result:
                    plot.append(viz.get_multi_table(self.result[id], identifier, self.args["title"]))
            elif name == "barplot":
                x_title = "x"
                y_title = "y"
                if "x_title" in self.args:
                    x_title = self.args["x_title"]
                if "y_title" in self.args:
                    y_title = self.args["y_title"]
                for id in self.result:
                    if isinstance(id, tuple):
                        identifier = identifier+"_"+id[0]+"_vs_"+id[1]
                        figure_title = self.args['title'] + id[0]+" vs "+id[1]
                    else:
                        figure_title = self.args['title']
                    self.args["title"] = figure_title
                    plot.append(viz.get_barplot(self.result[id], identifier, self.args))
            elif name == "facetplot":
                x_title = "x"
                y_title = "y"
                plot_type = "bar"
                if "x_title" not in self.args:
                    self.args["x_title"] = x_title
                if "y_title" not in self.args:
                    self.args["y_title"] = y_title
                if "plot_type" not in self.args:
                    self.args["plot_type"] = plot_type
                for id in self.result:
                    if isinstance(id, tuple):
                        identifier = identifier+"_"+id[0]+"_vs_"+id[1]
                        figure_title = self.args['title'] + id[0]+" vs "+id[1]
                    else:
                        figure_title = self.args['title']
                    self.args['title'] = figure_title
                    plot.append(viz.get_facet_grid_plot(self.result[id], identifier, self.args))
            elif name == "scatterplot":
                x_title = "x"
                y_title = "y"
                if "x_title" in self.args:
                    x_title = self.args["x_title"]
                if "y_title" in self.args:
                    y_title = self.args["y_title"]
                for id in self.result:
                    if isinstance(id, tuple):
                        identifier = identifier+"_"+id[0]+"_vs_"+id[1]
                        figure_title = self.args['title'] + id[0]+" vs "+id[1]
                    else:
                        figure_title = self.args['title']
                    self.args['title'] = figure_title
                    plot.append(viz.get_scatterplot(self.result[id], identifier, self.args))
            elif name == 'pca':
                x_title = "x"
                y_title = "y"
                if "x_title" in self.args:
                    x_title = self.args["x_title"]
                if "y_title" in self.args:
                    y_title = self.args["y_title"]
                for id in self.result:
                    if isinstance(id, tuple):
                        identifier = identifier+"_"+id[0]+"_vs_"+id[1]
                        figure_title = self.args['title'] + id[0]+" vs "+id[1]
                    else:
                        figure_title = self.args['title']
                    self.args['title'] = figure_title
                    plot.append(viz.get_pca_plot(self.result[id], identifier, self.args))
            elif name == "volcanoplot":
                alpha = 0.05
                lfc = 1.0
                if "alpha" not in self.args:
                    self.args["alpha"] = alpha
                if "lfc" not in self.args:
                    self.args["lfc"] = lfc
                for pair in self.result:
                    signature = self.result[pair]
                    self.args["title"] = self.args['title'] + " " + pair[0] + " vs " + pair[1]
                    p = viz.run_volcano(signature, identifier + "_" + pair[0] + "_vs_" + pair[1], self.args)
                    plot.extend(p)
            elif name == 'network':
                source = 'source'
                target = 'target'
                if "source" not in self.args:
                    self.args["source"] = source
                if "target" not in self.args:
                    self.args["target"] = target
                for id in self.result:
                    if isinstance(id, tuple):
                        identifier = identifier+"_"+id[0]+"_vs_"+id[1]
                        figure_title = self.args["title"] + id[0]+" vs "+id[1]
                    else:
                        figure_title = self.args["title"]
                    self.args["title"] = figure_title
                    plot.append(viz.get_network(self.result[id], identifier, self.args))
            elif name == "heatmap":
                for id in self.result:
                    if not self.result[id].empty:
                        if isinstance(id, tuple):
                            identifier = identifier+"_"+id[0]+"_vs_"+id[1]
                            figure_title = self.args["title"] + id[0]+" vs "+id[1]
                        else:
                            figure_title = self.args["title"]
                        self.args["title"] = figure_title
                        plot.append(viz.get_complex_heatmapplot(self.result[id], identifier, self.args))
            elif name == "mapper":
                for id in self.result:
                    labels = {}
                    if "labels" not in self.args:
                        self.args["labels"] = labels
                    if isinstance(id, tuple):
                        identifier = identifier+"_"+id[0]+"_vs_"+id[1]
                        figure_title = self.args['title'] + id[0]+" vs "+id[1]
                    else:
                        figure_title = self.args['title']
                    plot.append(viz.getMapperFigure(self.result[id], identifier, title=figure_title, labels=self.args["labels"]))
            elif name == "scatterplot_matrix":
                for id in self.result:
                    if isinstance(id, tuple):
                        identifier = identifier+"_"+id[0]+"_vs_"+id[1]
                        figure_title = self.args['title'] + id[0]+" vs "+id[1]
                    else:
                        figure_title = self.args['title']
                    self.args["title"] = figure_title
                    plot.append(viz.get_scatterplot_matrix(self.result[id], identifier, self.args))
            elif name == "distplot":
                for id in self.result:
                    if isinstance(id, tuple):
                        identifier = identifier+"_"+id[0]+"_vs_"+id[1]
                        figure_title = self.args['title'] + id[0]+" vs "+id[1]
                    else:
                        figure_title = self.args['title']
                    self.args["title"] = figure_title
                    plot.extend(viz.get_distplot(self.result[id], identifier, self.args))
            elif name == "violinplot":
                for id in self.result:
                    if isinstance(id, tuple):
                        identifier = identifier+"_"+id[0]+"_vs_"+id[1]
                        figure_title = self.args['title'] + id[0]+" vs "+id[1]
                    else:
                        figure_title = self.args['title']
                    self.args["title"] = figure_title
                    plot.extend(viz.get_violinplot(self.result[id], identifier, self.args))
            elif name == "polar":
                for id in self.result:
                    figure_title = self.args['title']
                    plot.append(viz.get_polar_plot(self.result[id], identifier, self.args))
            elif name == "km":
                for id in self.result:
                    plot.append(viz.get_km_plot(self.result[id], identifier, self.args))
            elif name == "wgcnaplots":
                start = time.time()
                data = {}
                sd_cutoff = 0
                input_data = self.data
                wgcna_data = self.result
                if 'sd_cutoff' in self.args:
                    sd_cutoff = self.args['sd_cutoff']
                if 'drop_cols_exp' in self.args and 'drop_cols_cli' in self.args:
                    #dfs = wgcna.get_data(input_data, drop_cols_exp=self.args['drop_cols_exp'], drop_cols_cli=self.args['drop_cols_cli'], sd_cutoff=sd_cutoff)
                    if 'wgcna' in wgcna_data and wgcna_data['wgcna'] is not None:
                        for dtype in wgcna_data['wgcna']:
                            data = wgcna_data['wgcna'][dtype]
                            plot.extend(viz.get_WGCNAPlots(data, identifier + "-" + dtype))
                print('WGCNA-plot', time.time() - start)
            elif name == 'ranking':
                for id in self.result:
                    plot.append(viz.get_ranking_plot(self.result[id], identifier, self.args))
            elif name == 'qcmarkers_boxplot':
                for id in self.result:
                    plot.append(viz.get_boxplot_grid(self.result[id], identifier, self.args))
            elif name == 'clustergrammer':
                for id in self.result:
                    plot.append(viz.get_clustergrammer_plot(self.result[id], identifier, self.args))
            elif name == 'cytonet':
                for id in self.result:
                    plot.append(viz.get_cytoscape_network(self.result[id], identifier, self.args))
            elif name == 'wordcloud':
                for id in self.result:
                    plot.append(viz.get_wordcloud(self.result[id], identifier, self.args))

        return plot
