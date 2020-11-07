const baseURL = window.location.origin;
const searchURL = baseURL + "/search";
const getURL = baseURL + "/nodes/";
const pageSize = 10;

export const getNodes = async (q, page, filters) => {
    let traversal = [];

    function addFieldFilter(field) {
        let value = filters[field];

        if (field && value) {
            if (field === "attributes") {

            } else {
                traversal.push({
                    "criteria": [
                        {
                            "type": "field",
                            "field": field,
                            "compare": "icontains",
                            "value": value,
                        }
                    ]
                });
            }
        }
    }

    Object.keys(filters).forEach(addFieldFilter);

    const body = {
        q: q,
        limit: pageSize,
        offset: page * pageSize,
        traversal: traversal,
    };

    return await callSearch(searchURL, "POST", body);
};

export const getEdges = async (key, page) => {
    const body = {
        q: key,
        input: 'key',
        traversal: [
            {
                directions: ['incoming', 'outgoing'],
                max_hops: 1,
            }
        ],
        limit: pageSize,
        offset: page * pageSize,
    };
    return await callSearch(searchURL, "POST", body);
};


export const getNode = async (key) => {
    return await callSearch(getURL + key, "GET", null);
};

export const callSearch = async (url, method, body) => {
    if (body) {
        body = JSON.stringify(body);
    }

    return await fetch(url, {
        method: method,
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        body: body,
    })
        .then(response => {
            return response.json()
        })
        .catch(async response => {
            console.log(response);
            return {"nodes": [], "trails": []};
        });
};
