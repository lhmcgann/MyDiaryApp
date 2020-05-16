import React, { Component } from 'react'

class DiaryButton extends Component {
  initialState = {
    name: '',
  }

  state = this.initialState
  handleChange = event => {
  const { name, value } = event.target

  this.setState({
    [name]: value,
  })
}
render() {
  const { name } = this.state;

  return (
    <form>
      <div class="entry-grid">
      <label htmlFor="name">Name</label>
      <input
        size= "10"
        type="text"
        name="name"
        id="name"
        value={name}
        onChange={this.handleChange} />
      <input type="button" value="+ Add Diary" onClick={this.submitForm} />
    </div>
    </form>

    );
  }
  submitForm = () => {
    this.props.handleSubmit(this.state)
    this.setState(this.initialState)
  }
}

export default DiaryButton;
