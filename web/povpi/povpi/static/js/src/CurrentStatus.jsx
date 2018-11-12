// CurrentStatus.jsx

import React from'react';
import{ withStyles } from'@material-ui/core/styles';
import Grid from'@material-ui/core/Grid';
import Card from'@material-ui/core/Card';
import CardContent from'@material-ui/core/CardContent';
import{ Message, PowerSettingsNew } from'@material-ui/icons';
import Typography from'@material-ui/core/Typography';
import{ green, red } from'@material-ui/core/colors';

import List from'@material-ui/core/List';
import ListItem from'@material-ui/core/ListItem';
import ListItemIcon from'@material-ui/core/ListItemIcon';
import ListItemSecondaryAction from'@material-ui/core/ListItemSecondaryAction';
import ListItemText from'@material-ui/core/ListItemText';
import ListSubheader from'@material-ui/core/ListSubheader';
import Switch from'@material-ui/core/Switch';

import axios from'axios';
import{ observable } from'mobx';
import{ observer } from'mobx-react';

const styles = (theme) => ({
  card: {
    minWidth: 275
  },
  bullet: {
    display: 'inline-block',
    transform: 'scale(2.5)',
    margin: '0 2px',
    color: green[500]
  },
  title: {
    fontSize: 14
  },
  powerIconOn: {
    color: green[500]
  },
  powerIconOff: {
    color: red[500]
  },
  pos: {
    marginBottom: 12
  },
  cardButton: {
    float: 'right'
  },
  statusMessage: {
    display: 'inline'
  }
});

@observer
class CurrentStatus extends React.Component {
  @observable
  powerStatus = false;

  togglePower = () => {
    this.powerStatus = !this.powerStatus;
    axios.post('/toggle', {
      state: this.powerStatus
    });
  };

  render() {
    const{ classes } = this.props;
    const power = this.powerStatus;
    return(
      <Card className={classes.card}>
        <CardContent>
          <Grid container spacing={8}>
            <Grid item xs={8}>
              <List subheader={<ListSubheader>Pi Status</ListSubheader>}>
                <ListItem>
                  <ListItemIcon>
                    <PowerSettingsNew
                      className={
                        power ? classes.powerIconOn : classes.powerIconOff
                      }
                    />
                  </ListItemIcon>
                  <ListItemText primary="Power" />
                  <ListItemSecondaryAction>
                    <Switch
                      color="primary"
                      onChange={() => this.togglePower()}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Message />
                  </ListItemIcon>
                  <ListItemText primary="Current Display" />
                  <ListItemSecondaryAction>
                    <Typography variant="h6">
                      {this.props.currentMessage}
                    </Typography>
                  </ListItemSecondaryAction>
                </ListItem>
              </List>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  }
}

export default withStyles(styles)(CurrentStatus);
