export class Entity {

    constructor(data) {
        this._data = data;
    }

    get key() {
        return this._data["key"];
    }

    set key(value) {
        this._data["key"] = value;
    }

    get label() {
        return this._data["label"];
    }

    set label(value) {
        this._data["label"] = value;
    }

    get name() {
        return this._data["name"];
    }

    set name(value) {
        this._data["name"] = value;
    }

    get attributes() {
        const attributes = {};

        for (const [key, value] of  Object.entries(this._data || {})) {
            if (!["key", "name", "label"].includes(key)) {
                if (value === '' || value === null || value === undefined) continue;
                if (value instanceof Array && value.length === 0) continue;
                attributes[key] = value;
            }
        }

        return Object.entries(attributes).sort();
    }

    get body() {
        const body = {};

        for (const [key, value] of  Object.entries(this._data || {})) {
            if (value === '' || value === null || value === undefined) continue;
            if (value instanceof Array && value.length === 0) continue;
            body[key] = value;
        }

        return body;
    }


}

export class Neighbor {

    constructor(trail, node) {
        const edge = trail.hops[0].edges[0];
        this.direction = edge.end === trail.end ? "outgoing" : "incoming";
        this.verb = edge.verb;
        this.key = node.key;
        this.label = node.label;
        this.name = node.name;
    }
}
