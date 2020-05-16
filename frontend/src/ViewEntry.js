import React, { Component } from "react";
class ViewEntry extends Component {
  initialState = {
    name: "",
  };

  state = this.initialState;
  handleChange = (event) => {
    const { name, value } = event.target;

    this.setState({
      [name]: value,
    });
  };
  render() {
    const { name } = this.state;

    return (
      <form>
        <label htmlFor="name">Name</label>
        <input
          type="text"
          name="name"
          id="name"
          value={name}
          onChange={this.handleChange}
        />
        <input type="button" value="Submit" onClick={this.submitForm} />
      </form>
    );
  }
  submitForm = () => {
    this.props.handleSubmit(this.state);
    this.setState(this.initialState);
  };
}
export default ViewEntry;
