import {wrap} from 'svelte-spa-router/wrap'

import DocFrame from "./views/DocFrame.svelte";
import NodeDetail from "./views/NodeDetail.svelte";
import NodeEdit from "./views/NodeEdit.svelte";
import ParseView from "./views/ParseView.svelte";
import NodeListing from "./views/NodeListing.svelte";

export default {
    // documentation
    '/api': wrap({
        component: DocFrame,
        props: {source: "/docs", title: "Swagger UI"}
    }),
    '/docs': wrap({
        component: DocFrame,
        props: {source: "https://www.entitykb.org/", title: "Documentation"}
    }),

    '/parse': ParseView,
    '/detail/:key': NodeDetail,

    '/edit/:key': NodeEdit,
    '/add/': NodeEdit,

    '*': NodeListing,
}