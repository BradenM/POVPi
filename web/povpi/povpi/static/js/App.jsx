// App.jsx

import React from'react';
import Dashboard from'./src/Dashboard';
import{ withStyles } from'@material-ui/core/styles';

export const get_url = (page) => {
  const href = window.location.href;
  let url = href + page;
  if(href[href.length - 1] !== '/') {
    url = href + '/' + page;
  }
  return url;
};

class App extends React.Component {
  render() {
    const{ classes } = this.props;
    return(
      <div className={classes.root}>
        <Dashboard />
      </div>
    );
  }
}

const styles = {
  root: {
    flexGrow: 1
  }
};

export default withStyles(styles)(App);
