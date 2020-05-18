import React, { Component } from "react";
import EntryList from "./EntryList"
import Button from "react-bootstrap/Button";
class DiaryHome extends Component {

constructor(props){
  super(props);
  this.state = {
      entries: [
        { title: "Entry  0", date: "1/3/19", tags: "Orange" },
        { title: "Entry  1", date: "1/1/19", tags: "Blue" },
        { title: "Entry  2", date: "1/4/19", tags: "Green" },
        { title: "Entry  3", date: "1/5/19", tags: "Red" },
        { title: "Entry  4", date: "1/2/19", tags: "Yellow" },
        { title: "Entry  5", date: "1/3/19", tags: "Orange" },
        { title: "Entry  6", date: "1/3/19", tags: "Orange" },
        { title: "Entry  7", date: "1/3/19", tags: "Orange" },
        { title: "Entry  8", date: "1/3/19", tags: "Orange" },
        { title: "Entry  9", date: "1/3/19", tags: "Orange" },
        { title: "Entry  10", date: "1/3/19", tags: "Orange" },
        { title: "Entry  11", date: "1/3/19", tags: "Orange" },
      ],
    };
  }
  render() {
    const { entries } = this.state;
    return (
      <div class="centered">
        <h1>{this.props.location.state}</h1>
        <EntryList entryData={entries} />
      </div>
    );
  }
}
export default DiaryHome;
