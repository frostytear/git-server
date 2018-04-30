const GRAPHQL_URL = 'http://graphql-private';
const graphqlClient = require('graphql-client')({url: GRAPHQL_URL});

function get(data, callback) {
  graphqlClient.query(`
  `, {
  }, function(req, res){
    if(res.status === 401) {
        throw new Error('Not authorized');
    }
  })
  .then(callback)
  .catch(function(err) {
      console.log(err.message)
  });
}
