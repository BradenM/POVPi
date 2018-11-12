// App.jsx

import React from'react';
import Dashboard from'./src/Dashboard';
import{ withStyles } from'@material-ui/core/styles';

class App extends React.Component {
  get_url(page) {
    const url = window.location.href + page;
    return url;
  }

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
