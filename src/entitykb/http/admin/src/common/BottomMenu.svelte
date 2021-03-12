<script>
    import {removeToken} from "../auth/token";
    import {replace, link} from "svelte-spa-router";

    const logout = async () => {
        removeToken();
        await replace("/");
    };
</script>


<div class="ui four item bottom fixed inverted menu">
    <a href={'#'} class="item" on:click={logout}>
        <i class="sign out alternative icon"></i> Logout
    </a>

<!--    <a href="/docs" class="item" use:link>-->
<!--        <i class="book open icon"></i> Docs-->
<!--    </a>-->

    <div class="item">
    </div>

    <div class="item">
    </div>

    <div class="item">
        <a href="https://www.entitykb.org/">
            <i class="large lightbulb outline icon"></i>
        </a>
        <a href="https://github.com/genomoncology/entitykb">
            <i class="large github icon"></i>
        </a>
        <a href="https://twitter.com/genomoncology">
            <i class="large twitter icon"></i>
        </a>
        <a href="https://www.linkedin.com/company/genomoncology">
            <i class="large linkedin icon"></i>
        </a>
        <a href="https://www.genomoncology.com">
            <i class="large globe icon"></i>
        </a>
    </div>
</div>