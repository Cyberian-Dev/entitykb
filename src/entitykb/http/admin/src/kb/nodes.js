function isAttribute(fieldName) {
    return !["key", "name", "label"].includes(fieldName);
}

export class Entity {

    constructor(data) {
        this.key = null;
        this.label = null;
        this.name = null;
        this.attributes = {};

        for (const [key, value] of Object.entries(data || {})) {
            if (isAttribute(key)) {
                if (value === '' || value === null || value === undefined) continue;
                if (value instanceof Array && value.length === 0) continue;
                this.attributes[key] = value;
            } else {
                this[key] = value;
            }
        }
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
