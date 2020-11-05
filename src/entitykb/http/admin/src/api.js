const baseURL = window.location.origin;
const searchURL = baseURL + "/search";
const pageSize = 10;

export const search = async (term, key, label, attr_name, attr_value, page) => {
    let traversal = [];

    if (key) {
        traversal.push({
            "criteria": [
                {
                    "type": "field",
                    "field": "key",
                    "compare": "icontains",
                    "value": key,
                }
            ]
        });
    }

    if (label) {
        traversal.push({
            "criteria": [
                {
                    "type": "field",
                    "field": "label",
                    "compare": "icontains",
                    "value": label,
                }
            ]
        });
    }

    if (attr_name && attr_value) {
        traversal.push({
            "criteria": [
                {
                    "type": "field",
                    "field": attr_name,
                    "compare": "icontains",
                    "value": attr_value,
                }
            ]
        });
    }

    const body = {
        'q': term,
        'limit': pageSize,
        'offset': page * pageSize,
        'traversal': traversal,
    };

    return await fetch(searchURL, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        body: JSON.stringify(body),
    })
        .then(response => {
            return response.json()
        })
        .catch(async response => {
            console.log(response);
            return {"nodes": [], "trails": []};
        });
};