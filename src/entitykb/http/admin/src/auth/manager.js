import {myToken} from "./token";

const baseURL = window.location.origin + "/";

export const loginUser = async (username, password) => {
    const url = 'token';
    const body = `username=${username}&password=${encodeURIComponent(password)}`;
    const contentType = 'application/x-www-form-urlencoded';
    const accessToken = await doFetch(url, body, contentType);

    let success = false;
    if (accessToken) {
        myToken.set(accessToken);
        success = true;
    }

    return success;
};

const doFetch = async (url, body, contentType) => {
    return await fetch(baseURL + url, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'include',
        headers: {
            'accept': 'application/json',
            'Content-Type': contentType,
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        body: body,
    })
        .then(async response => {
            const data = await response.json();
            return data.access_token;
        })
        .catch(async response => {
            console.log(response);
            return null;
        });
};