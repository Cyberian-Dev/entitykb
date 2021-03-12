<script>
    import {removeToken} from "../auth/token";
    import {replace, link} from "svelte-spa-router";

    const logout = async () => {
        removeToken();
        await replace("/");
    };
</script>

<div class="ui four item inverted menu">
    <a href="/" class="item" use:link>
        <i class="vector square icon"></i> Graph
    </a>

<!--    <a href="/add/" class="item" use:link>-->
<!--        <i class="plus circle icon"></i> Add Node-->
<!--    </a>-->

    <a href="/parse" class="item" use:link>
        <i class="highlighter icon"></i> Parse
    </a>

    <a href="/api" class="item" use:link>
        <i class="bolt icon"></i> API
    </a>

    <a href="/docs" class="item" use:link>
        <i class="book open icon"></i> Docs
    </a>

</div>
