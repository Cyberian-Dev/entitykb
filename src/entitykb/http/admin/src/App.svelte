<script>
    import {onMount} from "svelte";
    import {SvelteToast} from "@zerodevx/svelte-toast";

    import Router from 'svelte-spa-router';
    import routes from './routes';
    import AuthMain from "./auth/AuthMain.svelte";

    import {initToken} from "./auth/token";
    import {myToken} from "./auth/token";
    import {Schema} from "./kb/schema";
    import TopMenu from "./common/TopMenu.svelte";
    import BottomMenu from "./common/BottomMenu.svelte";

    onMount(async () => {
        await Schema.instance().load();
        await initToken();
    });

    let token = null;

    myToken.subscribe(
            newToken => {
                token = newToken;
            }
    );

    const options = {
        theme: {
            '--toastWidth': '20rem',
            '--toastHeight': '5rem'
        },
        duration: 1500
    }
</script>

{#if token}
    <TopMenu/>

    <div id="appContainer">
        <Router {routes}/>
    </div>

    <BottomMenu/>
{:else}
    <AuthMain/>
{/if}

<SvelteToast {options}/>

<style>
    #appContainer {
        margin-left: 2em;
        margin-right: 2em;
        padding-bottom: 5em;
    }
</style>
