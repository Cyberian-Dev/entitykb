import _ from 'underscore';
import {Entity, Neighbor} from "./nodes";
import {Comparison, FieldCriteria, SearchRequest, Traversal} from "./query";

const baseURL = window.location.origin;
const parseURL = baseURL + "/parse";
const searchURL = baseURL + "/search";
const getNodeURL = baseURL + "/nodes/";
const getSchemaURL = baseURL + "/meta/schema";

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

    constructor() {
        this.isClear = true;
        this.lastPage = null;
        this.lastRequest = {};
    }

    isAvailable(page, nextRequest) {
        const isChanged = (page !== this.lastPage) || (!_.isEqual(nextRequest, this.lastRequest));
        return this.isClear && isChanged
    }

    start(page, thisRequest) {
        this.isClear = false;
        this.lastPage = page;
        this.lastRequest = {...thisRequest};
    }

    finish() {
        this.isClear = true;
    }

    async getSchema() {
        return await fetch(getSchemaURL, {
            ...defaultParams,
            method: "GET",
        })
            .then(response => {
                return response.json()
            })
            .catch(async response => {
                console.log(response);
                return {}
            });
    }

    async getEntity(key) {
        const data = await fetch(getNodeURL + key, {
            ...defaultParams,
            method: "GET",
        })
            .then(response => {
                return response.json()
            })
            .catch(async response => {
                console.log(response);
                return {}
            });

        return new Entity(data);
    }

    async parseDoc(text) {
        const body = JSON.stringify({text: text});

        return await fetch(parseURL, {
            ...defaultParams,
            method: "POST",
            body: body,
        })
            .then(response => {
                return response.json()
            })
            .catch(async response => {
                console.log(response);
                return {
                    text: text,
                    spans: [],
                    tokens: []
                }
            });
    }

    async getDoc(page, thisRequest) {
        this.start(page, thisRequest);
        let doc = await this.parseDoc(thisRequest.text);
        this.finish();
        return doc;
    }

    async getNeighbors(page, thisRequest) {
        this.start(page, thisRequest);

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
        const request = new SearchRequest(null, null, keys, traversal, page);
        const response = await this.doSearch(request);

        let nodes = new Map(response.nodes.map(node => [node.key, node]));
        let neighbors = response.trails.map(trail => new Neighbor(trail, nodes.get(trail.end)));

        this.finish();
        return neighbors;
    }

    async getEntities(page, thisRequest) {
        this.start(page, thisRequest);

        let traversal = new Traversal();

        let labels = thisRequest.label ? [thisRequest.label] : [];
        let keys = thisRequest.key ? [thisRequest.key] : [];

        if (Boolean(thisRequest.attribute)) {
            const criteria = new FieldCriteria(
                thisRequest.attribute.name, Comparison.icontains, thisRequest.attribute.value
            );
            traversal.include([criteria]);
        }

        const request = new SearchRequest(thisRequest.name, labels, keys, traversal, page);
        const response = await this.doSearch(request);
        const entities = response.nodes.map(data => new Entity(data));

        this.finish();
        return entities;
    }

    async doSearch(request) {
        const body = JSON.stringify(request);

        return await fetch(searchURL, {
            ...defaultParams,
            method: "POST",
            body: body,
        })
            .then(response => {
                return response.json()
            })
            .catch(async response => {
                console.log(response);
                return {nodes: [], trails: []};
            });
    }
}