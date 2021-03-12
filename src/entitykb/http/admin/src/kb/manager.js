import {Entity, Neighbor} from "./nodes";
import {Comparison, FieldCriteria, SearchRequest, Traversal} from "./query";

const baseURL = window.location.origin;

const findOneURL = baseURL + "/find_one";
const getNodeURL = baseURL + "/nodes/";
const searchURL = baseURL + "/search";
const getSchemaURL = baseURL + "/meta/schema";
const parseURL = baseURL + "/parse";
const saveNodeURL = baseURL + "/nodes";


const defaultParams = {
    mode: 'cors',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
};

export class RequestManager {

    async getSchema() {
        return await fetch(getSchemaURL, {
            ...defaultParams,
            method: "GET",
        })
            .then(response => {
                if (!response.ok) {
                    return Promise.reject(response);
                }
                return response.json()
            })
            .catch(async response => {
                console.log(response);
                return {labels: [], verbs: []}
            });
    }

    async findOne(key) {
        const words = key.split("|");
        const text = words[0];
        const label = words[1];

        const body = JSON.stringify({text: text, labels: [label]});

        const data = await fetch(findOneURL, {
            ...defaultParams,
            method: "POST",
            body: body,
        })
            .then(response => {
                if (!response.ok) {
                    return Promise.reject(response);
                }
                return response.json()
            })
            .catch(async response => {
                console.log(response);
                return null;
            });

        return data ? new Entity(data) : null;
    }

    async getNode(key) {
        // double encoding required to send correctly.
        key = encodeURIComponent(encodeURIComponent(key));
        const data = await fetch(getNodeURL + key, {
            ...defaultParams,
            method: "GET",
        })
            .then(response => {
                if (!response.ok) {
                    return Promise.reject(response);
                }
                return response.json()
            })
            .catch(async response => {
                console.log(response);
                return null;
            });

        return data ? new Entity(data) : null;
    }

    async getNeighbors(thisRequest) {
        let traversal = new Traversal();
        traversal.walk(thisRequest.verb, thisRequest.direction);

        if (thisRequest.name) {
            const criteria = new FieldCriteria("name", Comparison.icontains, thisRequest.name);
            traversal.include([criteria]);
        }

        if (thisRequest.label) {
            const criteria = new FieldCriteria("label", Comparison.exact, thisRequest.label);
            traversal.include([criteria]);
        }


        let keys = thisRequest.key ? [thisRequest.key] : [];
        const request = new SearchRequest(null, null, keys, traversal, thisRequest.page);
        const response = await this.doSearch(request);

        if (response) {
            let nodes = new Map(response.nodes.map(node => [node.key, node]));
            return response.trails.map(trail => new Neighbor(trail, nodes.get(trail.end)));
        } else {
            return false;
        }
    }

    async getEntities(thisRequest) {
        let traversal = new Traversal();
        const request = new SearchRequest(
            thisRequest.q, thisRequest.labels, [], traversal, thisRequest.page
        );
        const response = await this.doSearch(request);
        if (response && response.nodes) {
            return response.nodes.map(data => new Entity(data));
        } else {
            return [];
        }
    }

    async doSearch(request) {
        const body = JSON.stringify(request);

        return await fetch(searchURL, {
            ...defaultParams,
            method: "POST",
            body: body,
        })
            .then(response => {
                if (!response.ok) {
                    return Promise.reject(response);
                }
                return response.json()
            })
            .catch(async response => {
                console.log(response);
                return {nodes: [], trails: []};
            });
    }

    async parseDoc(thisRequest) {
        const body = JSON.stringify(thisRequest);

        return await fetch(parseURL, {
            ...defaultParams,
            method: "POST",
            body: body,
        })
            .then(response => {
                if (!response.ok) {
                    return Promise.reject(response);
                }
                return response.json()
            })
            .catch(async response => {
                console.log(response);
                return {
                    text: thisRequest.text,
                    spans: [],
                    tokens: []
                }
            });
    }

    async saveEntity(entity) {
        const body = JSON.stringify(entity.body);

        return await fetch(saveNodeURL, {
            ...defaultParams,
            method: "POST",
            body: body,
        }).then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return false;
            }
        }).catch(async response => {
            console.log(response);
            return false;
        });
    }
}

export const manager = new RequestManager();