import React, { Component } from "react";
import EntryList from "./EntryList";
import Button from "react-bootstrap/Button";
class DiaryHome extends Component {
  state = {
    entries: [
      { name: "a" },
      { name: "b" },
      { name: "c" },
      { name: "d" },
      { name: "e" },
      { name: "f" },
      { name: "g" },
      { name: "h" },
    ],
  };
  render() {
    const { entries } = this.state;
    return (
      <div class="centered">
        <h1>{this.props.match.params.name}</h1>
        <EntryList entryData={entries} />
      </div>
    );
  }
}
export default DiaryHome;
