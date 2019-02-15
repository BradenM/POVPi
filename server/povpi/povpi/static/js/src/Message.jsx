// CurrentStatus.jsx
import React from'react';
import{ withStyles } from'@material-ui/core/styles';
import Grid from'@material-ui/core/Grid';
import Card from'@material-ui/core/Card';
import CardContent from'@material-ui/core/CardContent';

import TextField from'@material-ui/core/TextField';

import List from'@material-ui/core/List';
import ListItem from'@material-ui/core/ListItem';
import ListItemSecondaryAction from'@material-ui/core/ListItemSecondaryAction';
import ListSubheader from'@material-ui/core/ListSubheader';
import NavigationIcon from'@material-ui/icons/Navigation';
import Button from'@material-ui/core/Button';
import{ observable } from'mobx';
import{ observer } from'mobx-react';

const styles = {};

@observer
class MessageStatus extends React.Component {
  render() {
    const{ classes } = this.props;
    return(
      <Card>
        <CardContent>
          <Grid container spacing={8}>
            <Grid item xs={12}>
              <List subheader={<ListSubheader>Update Message</ListSubheader>}>
                <ListItem>
                  <form noValidate autoComplete="off">
                    <TextField
                      label="Message"
                      value={this.message}
                      margin="normal"
                      variant="filled"
                      fullWidth
                      onChange={this.props.handleChange()}
                      style={{
                        margin: 8,
                        paddingRight: '4em'
                      }}
                    />
                  </form>
                  <ListItemSecondaryAction style={{ marginLeft: '4em' }}>
                    <Button
                      variant="extendedFab"
                      aria-label="Delete"
                      color="primary"
                      onClick={() => this.props.handleSubmit()}
                    >
                      <NavigationIcon style={{ marginRight: '.3em' }} />
                      Send
                    </Button>
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

export default withStyles(styles)(MessageStatus);
