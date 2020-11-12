export class SearchRequest {
    constructor(q, labels, keys, traversal, page, pageSize) {
        pageSize = pageSize || 10;

        this.q = q || '';
        this.labels = labels || [];
        this.keys = keys || [];
        this.traversal = (traversal && traversal.steps) || [];
        this.limit = pageSize;
        this.offset = page * pageSize;
    }
}

export const Comparison = {
    contains: "contains",
    exact: "exact",
    gt: "gt",
    gte: "gte",
    icontains: "icontains",
    iexact: "iexact",
    is_in: "is_in",
    lt: "lt",
    lte: "lte",
    not_equal: "not_equal",
    startswith: "startswith",
    istartswith: "istartswith",
    endswith: "endswith",
    iendswith: "iendswith",
    range: "range",
    regex: "regex",
    iregex: "iregex",
};

export class FieldCriteria {
    
    constructor(field, compare = Comparison.exact, value = '') {
        this.field = field;
        this.compare = compare;
        this.value = value;
        this.type = "field";
    }
}

export class Traversal {

    constructor() {
        this.steps = [];
    }

    addStep(step) {
        this.steps = [...this.steps, step];
    }

    walk(verb = null, direction = null, maxHops = 1, passthru = false) {
        const verbs = verb !== null ? [verb] : [];
        const directions = Boolean(direction)  ? [direction.toLowerCase()] : ["incoming", "outgoing"];

        this.addStep({
            verbs: verbs,
            directions: directions,
            max_hops: maxHops,
            passthru: passthru,
        });
    }

    include(criteria = [], all = false) {
        this.addStep({
            criteria: criteria,
            all: all,
            exclude: false,
        });
    }

    exclude(criteria = [], all = false) {
        this.addStep({
            criteria: criteria,
            all: all,
            exclude: true,
        });
    }
}
