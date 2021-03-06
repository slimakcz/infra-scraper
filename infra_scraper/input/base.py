
import time
from infra_scraper.utils import setup_logger, get_graph_schema

logger = setup_logger('input.base')


class BaseInput(object):

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.config = kwargs['config']
        self.resources = {}
        self.resource_types = {}
        self.relations = {}
        self.timestamp = int(time.time())
        self._reverse_map = None
        self._schema = get_graph_schema(self.kind)

    def _create_relations(self):
        raise NotImplementedError

    def to_dict(self):
        self._create_relations()
        return {
            'name': self.name,
            'kind': self.kind,
            'timestamp': self.timestamp,
            'resource_types': self._get_resource_types(),
            'resources': self.resources,
            'relation_types': self._get_relation_types(),
            'relations': self.relations,
        }

    def _get_resource_types(self):
        res_map = {}
        for resource_name, resource in self.resources.items():
            res_map[resource_name] = self._schema['resource'][resource_name]
        return res_map

    def _get_relation_types(self):
        rel_map = {}
        for relation_name, relation in self.relations.items():
            rel_map[relation_name] = self._schema['relation'][relation_name]
        return rel_map

    def _get_resource_mapping(self):
        if self._reverse_map is None:
            self._reverse_map = {}
            for resource_name, resource in self._schema['resource'].items():
                self._reverse_map[resource['resource']] = resource_name
        return self._reverse_map

    def _scrape_resource(self, uid, name, kind, link=None, metadata={}):
        if kind not in self.resources:
            self.resources[kind] = {}
        self.resources[kind][uid] = {
            'uid': uid,
            'kind': kind,
            'name': name,
            'metadata': metadata,
        }

    def _scrape_relation(self, kind, source, target):
        if kind not in self.relations:
            self.relations[kind] = []
        self.relations[kind].append({
            'source': source,
            'target': target,
        })
