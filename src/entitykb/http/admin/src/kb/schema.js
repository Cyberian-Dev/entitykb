import {manager} from "./manager";

let _instance = null;

export class Schema {

    constructor() {
        this.data = null;
    }

    get labels() {
        return (this.data && this.data.labels) || [];
    }

    get verbs() {
        return (this.data && this.data.verbs) || [];
    }

    async load(force) {
        if (force || this.data === null) {
            this.data = await manager.getSchema();
        }
    }

    getNode(label) {
        return this.data.nodes[label];
    }

    get labelOptions() {
        const options = {};
        this.labels.map(label => {options[label] = label});
        return options;
    }
}

Schema.instance = () => {
    if (_instance === null) {
        _instance = new Schema();
    }
    return _instance;
};