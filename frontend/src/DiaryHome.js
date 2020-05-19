import React, { Component } from "react";
import EntryList from "./EntryList"
import Button from "react-bootstrap/Button";
class DiaryHome extends Component {

constructor(props){
  super(props);
  this.state = {
      entries: [],
    };
  }
  render() {
    const { entries } = this.state;
    return (
      <div class="centered">
        <h1>{this.props.location.title}</h1>
        <EntryList entryData={entries} />
      </div>
    );
  }
}
export default DiaryHome;
