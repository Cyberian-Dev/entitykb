import {toast} from "@zerodevx/svelte-toast";

export function toastSuccess(message) {
    toast.push(message, {
        theme: {
            '--toastBackground': '#48BB78',
            '--toastProgressBackground': '#2F855A',
        }
    })
}


export function toastFail(message) {
    toast.push(message, {
        theme: {
            '--toastBackground': '#F56565',
            '--toastProgressBackground': '#C53030',
        }
    })
}

export function toastClear() {
    toast.pop();
}

export function toastOnCondition(condition, message) {
    if (condition) {
        message += ": Success";
        toastSuccess(message);
    } else {
        message += ": Failed";
        toastFail(message);
    }
}