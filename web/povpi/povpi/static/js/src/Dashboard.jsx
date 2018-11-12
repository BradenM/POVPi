// App.jsx

import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import CurrentStatus from './CurrentStatus';
import MessageStatus from './Message';

const styles = theme => ({
  root: {
    flexGrow: 1
  },
  paper: {
    padding: theme.spacing.unit * 2,
    textAlign: 'center',
    color: theme.palette.text.secondary
  }
});

function Dashboard(props) {
  const { classes } = props;
  return (
    <div className={classes.root}>
      <Grid container spacing={24}>
        <Grid item xs={12}>
          <Typography variant="h2" color="inherit">
            PovPi Control
          </Typography>
        </Grid>
        <Grid item xs={6}>
          <MessageStatus />
        </Grid>
        <Grid item xs={6}>
          <CurrentStatus />
        </Grid>
      </Grid>
    </div>
  );
}

export default withStyles(styles)(Dashboard);
