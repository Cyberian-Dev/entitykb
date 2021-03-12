export class Edit {

    constructor(entity, schema) {
        this.entity = entity;
        this.schema = schema;
        this.definition = null;
        this.properties = null;
        this.loadDefinition();

    }

    get title() {
        const defTitle = (this.definition && this.definition.title) || "New";
        if (this.isNew) {
            return `Create ${defTitle}`;
        } else {
            return `Edit ${defTitle}: ${this.name}`;
        }
    }

    isRequired(name) {
        return (this.definition.required || []).includes(name);
    }

    get isNew() {
        const value = this.key;
        return (value === '' || value === null || value === undefined);
    }

    get name() {
        return this.entity && this.entity.name;
    }

    set name(value) {
        this.data["name"] = value;
    }

    get label() {
        return this.entity && this.entity.label;
    }

    set label(value) {
        this.data["label"] = value;
        this.loadDefinition();
    }

    get key() {
        return this.entity && this.entity.key;
    }

    get data() {
        return this.entity && this.entity._data;
    }

    get attributes() {
        const attributes = [];

        for (const [name, prop] of this.properties) {
            if (!["key", "name", "label"].includes(name)) {
                const type = prop["type"];
                const title = prop["title"];
                const required = this.isRequired(name);
                const value = this.data[name];
                const attr = {name, type, title, required, value};
                attributes.push(attr);
            }
        }

        return attributes;
    }

    loadDefinition() {
        this.definition = (this.label ? this.schema.getNode(this.label) : null) || this.schema.getNode("ENTITY");
        this.properties = ((this.definition && Object.entries(this.definition["properties"])) || []).sort();
    }

}