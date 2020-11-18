The recommended approach for iteratively developing and deploying EntityKB
is as follows:

1. Load data using the `entitykb load` tool.

2. Do initial development and unit testing using the in-memory `KB` class
   directly.
   
3. Run the development server using `entitykb dev`, view the web UI and
   test the HTTP API using the Swagger docs.
   
4. Do your application development in a separate project using the `SyncKB`
   or `AsyncKB` clients talking to the RPC server that is also running. 
   
5. In production, run the RPC server using `entitykb rpc` command.

### Additional Considerations

* Run EntityKB in a Docker container.

* Store the config.json and index.db in a read-only volume unless you 
  are sure you want to allow production updates. Your application must
  manage transactions and data integrity.
  
* Ensure your application handles security. Do not expose either the RPC
  or HTTP server ports to a non-trusted network. 

