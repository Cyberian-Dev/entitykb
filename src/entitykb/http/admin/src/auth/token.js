import {get, writable} from "svelte/store";

export const myToken = writable(null);

export const initToken = async () => {
    let token = localStorage.getItem("Token");
    myToken.set(token);
};

export const getMyToken = () => {
    return get(myToken);
};

myToken.subscribe(newToken => {
    if (newToken !== null) {
        localStorage.setItem("Token", newToken);
    }
});

export const removeToken = () => {
    myToken.set(null);
    localStorage.removeItem("Token");
};
