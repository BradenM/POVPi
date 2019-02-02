// App.jsx

import React from'react';
import{ withStyles } from'@material-ui/core/styles';
import Grid from'@material-ui/core/Grid';
import Typography from'@material-ui/core/Typography';
import CurrentStatus from'./CurrentStatus';
import MessageStatus from'./Message';
import{ observable } from'mobx';
import{ observer } from'mobx-react';
import axios from'axios';

const styles = (theme) => ({
  root: {
    flexGrow: 1
  },
  paper: {
    padding: theme.spacing.unit * 2,
    textAlign: 'center',
    color: theme.palette.text.secondary
  }
});

@observer
class Dashboard extends React.Component {
  @observable
  newMessage = '';

  @observable
  message = 'Hello World';

  handleMessageChange = (message) => (event) => {
    this.newMessage = event.target.value;
  };

  handleMessageSubmit = () => {
    this.message = this.newMessage;
    axios.post(window.location.href + '/change', {
      message: this.message
    });
  };

  render() {
    const{ classes } = this.props;
    return(
      <div className={classes.root}>
        <Grid container spacing={24}>
          <Grid item xs={12}>
            <Typography variant="h2" color="inherit">
              PovPi Control
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <MessageStatus
              handleChange={() => this.handleMessageChange()}
              handleSubmit={() => this.handleMessageSubmit()}
            />
          </Grid>
          <Grid item xs={6}>
            <CurrentStatus currentMessage={this.message} />
          </Grid>
        </Grid>
      </div>
    );
  }
}

export default withStyles(styles)(Dashboard);
